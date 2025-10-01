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