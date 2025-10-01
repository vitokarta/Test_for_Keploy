#!/bin/bash

echo "🧹 開始清理 Keploy 測試環境..."

# 停止容器
echo "📦 停止容器..."
docker compose down

# 刪除容器
echo "🗑️ 刪除容器..."
docker rm -f student-backend student-mysql 2>/dev/null || true

# 刪除網路
echo "🌐 刪除網路..."
docker network rm keploy-network 2>/dev/null || true

# 刪除鏡像
echo "🖼️ 刪除鏡像..."
docker rmi test_for_keploy-student-backend 2>/dev/null || true

# 刪除 Volume（可選，會清除資料庫資料）
read -p "是否刪除資料庫資料? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "💾 刪除資料庫 Volume..."
    docker volume rm test_for_keploy_mysql_data 2>/dev/null || true
fi

# 刪除 Keploy 測試資料
read -p "是否刪除 Keploy 測試資料? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📊 刪除 Keploy 測試資料..."
    rm -rf keploy/
fi

echo "✅ 清理完成！"
echo ""
echo "🚀 現在可以按照 README.md 重新開始："
echo "1. docker network create keploy-network"
echo "2. docker compose up mysql -d"
echo "3. keploy record ..."