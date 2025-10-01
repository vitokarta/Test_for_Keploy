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
keploy record -c "docker compose up" --container-name "student-backend" -n "keploy-network" --buildDelay 60

keploy record -c "docker compose up student-backend" --container-name "student-backend" -n "keploy-network" --buildDelay 60


## 測試方式

### 使用 Mock 數據測試（默認，推薦）
```bash
keploy test -c "docker compose up" --container-name "student-backend" -n "keploy-network" --delay 10 --buildDelay 60

# without mock
keploy test -c "docker compose up student-backend" --container-name "student-backend" --pass-through-ports 3306 -n "keploy-network"  -t "test-set-1"

```
### 使用真實資料庫測試（推薦）
```bash
#先啟動 MySQ
docker compose up mysql -d

keploy test -c "docker compose up student-backend" --container-name "student-backend" -n "keploy-network" --delay 10 --buildDelay 60

keploy test -c "docker compose up student-backend" --container-name "student-backend" --mocking=false --delay 10 --buildDelay 60

```
**重要**：使用外部網路 `keploy-network`，需要先創建：
```bash

docker network inspect keploy-network

docker network create keploy-network

docker network rm keploy-network

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