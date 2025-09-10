#!/bin/bash

echo "🐰 執行 Keploy 測試..."

# 確保應用正在運行
docker-compose -f docker-compose.keploy.yml up -d

# 等待應用啟動
sleep 5

# 執行 Keploy 測試
docker run --rm -it \
  --name keploy-test \
  -v $(pwd)/keploy-tests:/tmp/keploy-tests \
  --network keploy-network \
  ghcr.io/keploy/keploy:latest \
  test \
  -c "curl -X GET http://fastapi-app:8001/" \
  --container-name fastapi-app

echo "測試完成！"