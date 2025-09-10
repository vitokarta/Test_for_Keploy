#!/bin/bash

echo "🐰 啟動 FastAPI 應用和 Keploy 錄製模式..."

# 創建 keploy 測試目錄
mkdir -p keploy-tests

# 創建 Docker 網絡
docker network create keploy-network 2>/dev/null || echo "網絡已存在"

# 啟動 FastAPI 應用
echo "啟動 FastAPI 應用..."
docker-compose -f docker-compose.keploy.yml up -d

# 等待應用啟動
sleep 5

# 啟動 Keploy 錄製
echo "啟動 Keploy 錄製模式..."
docker run --rm -it \
  --name keploy-record \
  -v $(pwd)/keploy-tests:/tmp/keploy-tests \
  --network keploy-network \
  ghcr.io/keploy/keploy:latest \
  record \
  -c "curl -X GET http://fastapi-app:8001/" \
  --container-name fastapi-app

echo "錄製已停止。你可以使用 ./keploy-test.sh 來執行測試"