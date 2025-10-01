# Student Management System - Keploy API 測試專案

使用 Keploy 進行 FastAPI 學生管理系統的 API 測試，支援 Mock 和真實資料庫測試。

## 🚀 快速開始

### 1. 取得專案
```bash
git clone https://github.com/vitokarta/Test_for_Keploy.git
cd Test_for_Keploy
```

### 2. 安裝 Keploy
```bash
# macOS
curl --silent -O -L https://keploy.io/install.sh && source install.sh
```

### 3. 準備環境

#### 建立 Docker 網路
```bash
docker network create keploy-network
```

#### 啟動資料庫
```bash
docker compose up mysql -d
```

#### 準備前端（選用）
```bash
cd frontend
python3 -m http.server 8080
```

## 📹 錄製 API 測試

### 啟動錄製模式
```bash
keploy record -c "docker compose up student-backend" --container-name "student-backend" -n "keploy-network" --buildDelay 60
```

### 執行 API 操作
**方法一：使用前端網頁**
1. 打開 `http://localhost:8080`
2. 進行新增、編輯、刪除學生等操作

**方法二：使用 curl 命令**
```bash
# 查詢學生列表
curl http://localhost:8001/students/

# 新增學生
curl -X POST http://localhost:8001/students/ \
  -H "Content-Type: application/json" \
  -d '{"name": "測試學生", "email": "test@example.com", "password": "123456"}'

# GPA 計算
curl -X POST http://localhost:8001/students/1/calculate-gpa \
  -H "Content-Type: application/json" \
  -d '[85.5, 92.0, 78.3, 88.7, 91.2]'
```

### 停止錄製
按 `Ctrl+C` 終止錄製，測試案例會儲存在 `keploy/test-set-x/` 目錄

## 🧪 執行測試

### Mock 測試（快速）
使用錄製的資料進行測試：
```bash
keploy test -c "docker compose up student-backend" --container-name "student-backend" -n "keploy-network" --delay 10 --buildDelay 60
```

### 真實資料庫測試
#### 方法一：Pass-through（推薦）
```bash
keploy test -c "docker compose up student-backend" --container-name "student-backend" -n "keploy-network" --delay 10 --buildDelay 60 --pass-through-ports 3306
```

#### 方法二：完全關閉 Mock
```bash
keploy test -c "docker compose up student-backend" --container-name "student-backend" -n "keploy-network" --delay 10 --buildDelay 60 --mocking=false
```

### 🔧 可選參數
- `-t "test-set-1"` - 指定特定的測試集（預設執行所有測試集）
- `--delay 30` - 增加等待時間（如遇到啟動超時）
- `--buildDelay 120` - 增加容器建置時間

## 📊 查看結果

測試報告位於：`keploy/reports/test-run-x/`
- **test-set-0-report.yaml** - 詳細測試結果
- **coverage.txt** - 程式碼覆蓋率

## 🛠️ 故障排除

### 重置環境
```bash
# 停止所有容器
docker compose down

# 重建網路
docker network rm keploy-network
docker network create keploy-network

# 重新啟動
docker compose up mysql -d
```

## 📁 專案結構

```
├── backend/           # FastAPI 後端 + MySQL
├── frontend/          # 前端介面
├── keploy/           # Keploy 測試資料
│   ├── test-set-0/   # 錄製的測試案例
│   └── reports/      # 測試報告
├── docker-compose.yml
└── README.md
```

## 🔧 技術配置

- **後端**: FastAPI + SQLAlchemy + MySQL
- **前端**: HTML + JavaScript
- **網路**: Docker Bridge (172.18.0.0/16)
- **測試**: Keploy 2.11.1+