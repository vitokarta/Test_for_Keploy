# Keploy 外部 API 錄製配置指南

本文檔說明如何配置 Keploy 以正確錄製和測試外部 HTTPS API 調用（如 GitHub API）。

## 問題背景

當應用程序調用外部 HTTPS API 時，Keploy 需要攔截這些 TLS/SSL 連接。如果沒有正確配置，會出現以下錯誤：

```
ERROR   failed to complete TLS handshake with the client        {"error": "EOF"}
INFO:   172.18.0.3:16789 - "GET /github/user/vitokarta HTTP/1.1" 503 Service Unavailable
```

## 解決方案

### 1. 修改 Dockerfile

在 `backend/Dockerfile` 中添加 Keploy CA 證書支持：

```dockerfile
FROM python:3.12-slim

# 安裝 CA 證書工具
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 添加 Keploy CA 證書和設置腳本
ADD https://raw.githubusercontent.com/keploy/keploy/refs/heads/main/pkg/core/proxy/tls/asset/ca.crt ca.crt
ADD https://raw.githubusercontent.com/keploy/keploy/refs/heads/main/pkg/core/proxy/tls/asset/setup_ca.sh setup_ca.sh
RUN chmod +x setup_ca.sh

EXPOSE 8001

# 執行 CA 設置腳本後啟動應用
CMD ["/bin/bash", "-c", "source ./setup_ca.sh && python main.py"]
```

**關鍵修改**：
- 安裝 `ca-certificates` 套件
- 下載 Keploy 的 CA 證書文件 (`ca.crt`)
- 下載 Keploy 的證書設置腳本 (`setup_ca.sh`)
- 在啟動應用前執行設置腳本

### 2. 配置 Python httpx 使用 CA 證書

在 `backend/main.py` 中修改外部 API 調用代碼：

```python
@app.get("/github/user/{username}")
async def get_github_user(username: str):
    """取得 GitHub 用戶資訊 - 用於測試外部 API 調用"""
    # 使用 Keploy CA 證書（如果存在）
    import os
    ca_bundle = os.getenv("REQUESTS_CA_BUNDLE", "/tmp/ca.crt")
    verify = ca_bundle if os.path.exists(ca_bundle) else True

    async with httpx.AsyncClient(verify=verify) as client:
        try:
            response = await client.get(f"https://api.github.com/users/{username}")
            # ... 處理回應
```

**關鍵修改**：
- 讀取 `REQUESTS_CA_BUNDLE` 環境變數（由 `setup_ca.sh` 設置）
- 將 CA 證書路徑傳給 `httpx.AsyncClient(verify=ca_bundle)`
- 如果證書不存在，使用預設的系統證書

### 3. 安裝依賴

確保 `requirements.txt` 包含 `httpx`：

```txt
httpx==0.25.2
```

### 4. 重新構建 Docker 映像檔

```bash
docker compose down
docker compose build --no-cache student-backend
```

## 工作原理

1. **setup_ca.sh 腳本**會：
   - 將 Keploy CA 證書添加到系統證書庫
   - 設置環境變數：
     - `REQUESTS_CA_BUNDLE=/tmp/ca.crt`（Python requests/httpx）
     - `NODE_EXTRA_CA_CERTS=/tmp/ca.crt`（Node.js）

2. **應用程序啟動時**：
   - Keploy CA 證書已被信任
   - httpx 使用此證書驗證 HTTPS 連接
   - Keploy 可以成功攔截和記錄外部 API 調用

3. **錄製模式**：
   - Keploy 攔截 HTTPS 請求
   - 使用自己的 CA 證書建立 TLS 連接
   - 轉發請求到真實的 GitHub API
   - 記錄請求和回應作為 Mock


## 參考資料

- [Keploy TLS Docker Support](https://keploy.io/docs/running-keploy/docker-tls/)
- [httpx SSL 配置](https://www.python-httpx.org/advanced/#ssl-certificates)
