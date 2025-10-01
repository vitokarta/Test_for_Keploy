import pytest
import requests
import json
import time
from sqlalchemy import create_engine, text
from database import DATABASE_URL

class TestRealIntegration:
    """
    基於 Keploy 錄製內容的真實 integration 測試
    測試真實的數據庫操作和服務互動
    """

    @pytest.fixture(scope="class")
    def setup_database(self):
        """清理和準備測試數據庫"""
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # 清理測試數據
            conn.execute(text("DELETE FROM students WHERE email LIKE 'test%'"))
            conn.commit()

            # 插入初始測試數據（基於錄製內容）
            conn.execute(text("""
                INSERT INTO students (id, name, email, password) VALUES
                (1, '測試學生', 'test@example.com', 'password'),
                (3, '123', '123@gmail.com', 'password')
            """))
            conn.commit()
        yield
        # 測試後清理
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM students WHERE email LIKE 'test%'"))
            conn.commit()

    def test_get_students_real_db(self, setup_database):
        """測試 GET /students/ - 使用真實數據庫"""
        # 基於 test-1.yaml 的請求
        response = requests.get("http://localhost:8001/students/")

        assert response.status_code == 200
        data = response.json()

        # 驗證真實數據庫返回
        assert len(data) >= 2
        emails = [student['email'] for student in data]
        assert 'test@example.com' in emails
        assert '123@gmail.com' in emails

    def test_create_student_real_db(self, setup_database):
        """測試 POST /students/ - 真實創建學生"""
        # 基於 test-3.yaml 的請求
        payload = {
            "name": "test1",
            "email": "test@gmail.com",
            "password": "12345"
        }

        response = requests.post(
            "http://localhost:8001/students/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data['name'] == 'test1'
        assert data['email'] == 'test@gmail.com'
        assert 'id' in data

        # 驗證真實寫入數據庫
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM students WHERE email = :email"),
                {"email": "test@gmail.com"}
            )
            student = result.fetchone()
            assert student is not None
            assert student.name == 'test1'

    def test_delete_student_real_db(self, setup_database):
        """測試 DELETE /students/{id} - 真實删除學生"""
        # 先創建一個學生
        payload = {"name": "to_delete", "email": "delete@test.com", "password": "123"}
        create_response = requests.post("http://localhost:8001/students/", json=payload)
        student_id = create_response.json()['id']

        # 基於 test-6.yaml 的删除請求
        response = requests.delete(f"http://localhost:8001/students/{student_id}")

        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Student deleted successfully'

        # 驗證真實從數據庫删除
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM students WHERE id = :id"),
                {"id": student_id}
            )
            assert result.fetchone() is None

    def test_full_workflow_real_services(self, setup_database):
        """測試完整工作流程 - 所有服務真實運行"""
        # 1. 查詢初始學生列表
        initial_response = requests.get("http://localhost:8001/students/")
        initial_count = len(initial_response.json())

        # 2. 創建新學生
        new_student = {
            "name": "workflow_test",
            "email": "workflow@test.com",
            "password": "workflow123"
        }
        create_response = requests.post("http://localhost:8001/students/", json=new_student)
        assert create_response.status_code == 201
        student_id = create_response.json()['id']

        # 3. 驗證學生列表增加
        after_create_response = requests.get("http://localhost:8001/students/")
        assert len(after_create_response.json()) == initial_count + 1

        # 4. 計算 GPA（如果有多個服務整合）
        grades = [85.5, 92.0, 78.3, 88.7, 91.2]
        gpa_response = requests.post(
            f"http://localhost:8001/students/{student_id}/calculate-gpa",
            json=grades
        )
        assert gpa_response.status_code == 200

        # 5. 删除學生
        delete_response = requests.delete(f"http://localhost:8001/students/{student_id}")
        assert delete_response.status_code == 200

        # 6. 驗證學生列表恢復
        final_response = requests.get("http://localhost:8001/students/")
        assert len(final_response.json()) == initial_count

if __name__ == "__main__":
    # 運行測試前確保服務已啟動
    print("確保所有服務已啟動: docker compose up -d")
    time.sleep(2)

    # 檢查服務可用性
    try:
        response = requests.get("http://localhost:8001/students/", timeout=5)
        print(f"Service check: {response.status_code}")
    except Exception as e:
        print(f"Service not available: {e}")
        exit(1)