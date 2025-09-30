# Keploy 使用指南

## 啟動方式

### 1. 啟動應用程式
```bash
docker-compose up
```

### 2. 確認服務運行
- API 服務：http://localhost:8001
- MySQL 資料庫：localhost:3306

## 關閉容器

```bash
docker-compose down
```

## 錄製方式

### 使用 Keploy 監聽主程式
```bash
keploy record -c "docker-compose up student-backend" --container-name "student-backend" --buildDelay 60

keploy record -c "docker compose up" --container-name "student-backend" -n "keploy-network" --buildDelay 60

keploy record -c "docker run -p 8001:8001 --name student-backend --network keploy-network student-api:latest" \
--container-name "student-backend" --buildDelay 60


```

### API 測試端點

#### 建立學生
```bash
curl -X POST "http://localhost:8001/students/" \
  -H "Content-Type: application/json" \
  -d '{"name": "張小明", "email": "ming@example.com", "password": "password123"}'
```

#### 查詢學生
```bash
curl "http://localhost:8001/students/"
```

#### GPA 計算
```bash
curl -X POST "http://localhost:8001/students/1/calculate-gpa" \
  -H "Content-Type: application/json" \
  -d '[85.5, 92.0, 78.3, 88.7, 91.2]'
```

## 測試方式

### 使用 Mock 數據測試（默認，推薦）
```bash
keploy test -c "docker compose up" --container-name "student-backend" -n "keploy-network" --delay 10 --buildDelay 60
```

### 使用真實資料庫測試（需要分步驟）
```bash
# 步驟1：先啟動 MySQL
docker compose up mysql -d

# 步驟2：等待 MySQL 完全啟動
sleep 15

# 步驟3：測試後端（連接真實資料庫）
keploy test -c "docker compose up student-backend" --container-name "student-backend" --mocking=false --delay 30 --buildDelay 120
```

### 測試結果說明
- **Mock 測試**：使用錄製的數據，測試 API 邏輯和響應格式
- **真實資料庫測試**：驗證完整的資料庫操作流程