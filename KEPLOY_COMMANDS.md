# Keploy 指令使用說明

## 🚀 基本指令

### 錄製測試案例
```bash
keploy record -c "docker run -p 8001:8001 --name student-backend --network keploy-network student-api:latest" \
--container-name "student-backend" --buildDelay 60
```

### 執行測試
```bash
keploy test -c "docker run -p 8001:8001 --name student-backend --network keploy-network student-api:latest" \
--delay 10 --buildDelay 60
```

## 🔧 Docker 相關

### 建立 Docker Image
```bash
cd backend
docker build -t student-api:latest .
```

### 建立網路
```bash
docker network create keploy-network
```

### 查看容器狀態
```bash
docker ps -a
```

## 📂 檔案結構

```
backend/
├── keploy/
│   ├── test-set-0/
│   │   └── tests/          # 錄製的測試案例
│   └── reports/            # 測試報告
├── Dockerfile
├── main.py
└── requirements.txt
```

## 💡 使用流程

1. **錄製**: 執行 `keploy record`
2. **操作**: 使用 API 進行各種操作
3. **停止**: 按 `Ctrl+C` 停止錄製
4. **測試**: 執行 `keploy test` 驗證功能