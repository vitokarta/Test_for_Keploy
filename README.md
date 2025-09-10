# Student Management System - Keploy API 測試演示

這是一個專為測試 [Keploy](https://keploy.io) API 測試工具設計的前後端分離專案。Keploy 是一個 AI 驅動的測試工具，能夠自動錄製 API 調用並生成測試案例。

## 專案結構

```
project/
├── backend/                 # FastAPI 後端
│   ├── main.py             # FastAPI 主程式
│   ├── models.py           # 資料模型
│   ├── database.py         # 資料庫配置
│   ├── requirements.txt    # Python 依賴
│   └── students.db         # SQLite 資料庫 (啟動後自動生成)
├── frontend/               # 前端介面
│   ├── index.html         # 主頁面
│   ├── app.js            # JavaScript 邏輯
│   └── style.css         # 樣式
└── README.md             # 本文件
```

## 功能特色

### 後端 API (FastAPI)
- ✅ **學生 CRUD 操作**
- ✅ **SQLite 資料庫**
- ✅ **CORS 支持**
- ✅ **資料驗證**
- ✅ **錯誤處理**

### 前端介面
- ✅ **響應式設計**
- ✅ **即時 API 狀態檢查**
- ✅ **完整的 CRUD 操作**
- ✅ **友好的用戶體驗**

## 環境需求

- Python 3.8+
- 現代瀏覽器 (Chrome, Firefox, Safari, Edge)
- 支援 Keploy 的作業系統：
  - Linux (Kernel 5.15+)
  - macOS (使用 Docker Desktop 4.25.2+)
  - Windows (使用 WSL 2)

## 快速開始

### 1. 安裝 Python 依賴

```bash
cd backend
pip install -r requirements.txt
```

### 2. 啟動後端服務

```bash
cd backend
python main.py
# 或使用 uvicorn
uvicorn main:app --reload
```

後端將在 `http://localhost:8000` 啟動

### 3. 啟動前端

開啟瀏覽器並打開 `frontend/index.html` 文件，或使用簡單的 HTTP 服務器：

```bash
cd frontend
python -m http.server 8080
```

前端將在 `http://localhost:8080` 可用

## Keploy 測試指南

### 重要提醒：macOS 使用者

在 macOS 上，Keploy **無法直接使用命令行模式**，需要使用 Docker 版本。我們已經為您準備好所有必要的 Docker 配置文件。

### 安裝需求

#### macOS 用戶（推薦）
- **Docker Desktop 4.25.2+** ✅ 已檢測到您的版本符合要求
- 不需要單獨安裝 Keploy CLI

#### Linux 用戶
```bash
curl --silent -O -L https://keploy.io/install.sh && source install.sh
```

#### Windows (WSL 2)
1. 先確保已安裝 WSL 2
2. 在 WSL 2 中執行上述安裝命令

### macOS 使用 Docker 版本

我們已經為您創建了完整的 Docker 設置，使用方式：

#### 方法 1: 簡易啟動（推薦）
```bash
# 啟動 FastAPI 應用
docker-compose -f docker-compose.keploy.yml up -d

# 檢查應用狀態
curl http://localhost:8001

# API 文檔
open http://localhost:8001/docs
```

#### 方法 2: 使用 Keploy Docker 錄製

創建網絡並啟動錄製：
```bash
# 創建 Docker 網絡
docker network create keploy-network

# 啟動應用
docker-compose -f docker-compose.keploy.yml up -d

# 使用 Keploy Docker 錄製
mkdir -p keploy-tests
docker run --rm -it \
  -v $(pwd)/keploy-tests:/tmp/keploy-tests \
  --network test_for_keploy_keploy-network \
  ghcr.io/keploy/keploy:latest \
  record -c "sleep 30" --container-name test_for_keploy-fastapi-app-1
```

### Linux 使用原生版本

#### 步驟 1: 使用 Keploy 啟動後端

```bash
cd backend
keploy record -c "python main.py"
```

#### 步驟 2: 進行 API 測試

現在您可以通過以下方式生成測試案例：

**方法 1: 使用前端介面**
1. 開啟 `frontend/index.html`
2. 執行各種操作（新增、編輯、刪除學生）
3. Keploy 會自動錄製所有 API 調用

**方法 2: 使用 curl 命令**

```bash
# 1. 新增學生
curl -X POST "http://localhost:8000/students/" \
     -H "Content-Type: application/json" \
     -d '{"name": "王小明", "email": "ming@example.com", "password": "password123"}'

# 2. 獲取所有學生
curl -X GET "http://localhost:8000/students/"

# 3. 獲取單一學生
curl -X GET "http://localhost:8000/students/1"

# 4. 更新學生
curl -X PUT "http://localhost:8000/students/1" \
     -H "Content-Type: application/json" \
     -d '{"name": "王小明更新", "email": "ming.updated@example.com"}'

# 5. 刪除學生
curl -X DELETE "http://localhost:8000/students/1"
```

#### 步驟 3: 執行測試

停止錄製模式 (Ctrl+C)，然後執行生成的測試：

```bash
keploy test -c "python main.py" --delay 10
# 或
keploy test -c "uvicorn main:app --reload" --delay 10
```

### 查看測試結果

Keploy 將：
- 📊 顯示測試覆蓋率
- ✅ 驗證 API 響應
- 🔍 比較實際和預期結果
- 📝 生成詳細的測試報告

## API 端點說明

| 方法 | 端點 | 描述 |
|------|------|------|
| GET | `/` | API 狀態檢查 |
| POST | `/students/` | 新增學生 |
| GET | `/students/` | 獲取所有學生 |
| GET | `/students/{id}` | 獲取指定學生 |
| PUT | `/students/{id}` | 更新學生資訊 |
| DELETE | `/students/{id}` | 刪除學生 |

### 學生資料格式

```json
{
  "name": "學生姓名",
  "email": "student@example.com",
  "password": "密碼"
}
```

## 疑難解答

### 常見問題

**Q: Keploy 錄製時出現權限錯誤？**
A: 確保以適當權限執行 Keploy，某些系統可能需要 sudo。

**Q: API 無法連接？**
A: 檢查後端是否在 port 8000 運行，防火牆是否阻擋連接。

**Q: 前端顯示 CORS 錯誤？**
A: 確保後端已正確配置 CORS（已在 main.py 中配置）。

**Q: 測試執行失敗？**
A: 確保資料庫處於乾淨狀態，或調整 --delay 參數。

### Keploy 相關

**Q: Keploy 無法在 macOS/Windows 執行？**
A: 確保使用 Docker Desktop 4.25.2+ 或 WSL 2。

**Q: 測試案例沒有生成？**
A: 確保在錄製模式下進行了足夠的 API 調用。

## 進階使用

### 自訂測試場景

您可以創建更複雜的測試場景：

1. **資料完整性測試**: 新增學生後立即查詢驗證
2. **錯誤處理測試**: 嘗試重複新增相同 email 的學生
3. **批次操作測試**: 連續新增多個學生然後批次查詢

### 整合到 CI/CD

將 Keploy 測試整合到您的持續整合流程：

```yaml
# GitHub Actions 示例
- name: Run Keploy Tests
  run: |
    keploy test -c "python main.py" --delay 10
```

## 學習資源

- [Keploy 官方文件](https://docs.keploy.io/)
- [FastAPI 文件](https://fastapi.tiangolo.com/)
- [Keploy GitHub](https://github.com/keploy/keploy)

## 貢獻指南

歡迎提交 Issue 和 Pull Request 來改進此演示專案！

## 授權

此專案僅供學習和演示 Keploy 功能使用。