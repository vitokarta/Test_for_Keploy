#!/bin/bash

echo "🐰 Keploy Docker 版本設置指南"
echo "=================================="

# 檢查 Docker 是否運行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未運行，請先啟動 Docker Desktop"
    exit 1
fi

echo "✅ Docker 正在運行"

# 創建必要的目錄
mkdir -p keploy-tests

# 創建 Docker 網絡
echo "🌐 創建 Docker 網絡..."
docker network create keploy-network 2>/dev/null || echo "網絡已存在"

echo ""
echo "📋 使用方式："
echo "1. 錄製模式（推薦使用簡化方式）："
echo "   docker-compose -f docker-compose.keploy.yml up -d"
echo "   # 然後使用前端或 curl 調用 API"
echo ""
echo "2. 或者使用 Keploy 直接錄製："
echo "   ./start-record.sh"
echo ""
echo "3. 測試已錄製的案例："
echo "   ./start-test.sh"
echo ""
echo "首先讓我們先建構應用映像..."

# 建構 Docker 映像
docker-compose -f docker-compose.keploy.yml build

echo ""
echo "🚀 Ready! 現在你可以："
echo "1. 執行 'docker-compose -f docker-compose.keploy.yml up' 啟動應用"
echo "2. 使用瀏覽器打開 http://localhost:8001 測試 API"
echo "3. 或直接執行: curl http://localhost:8001/"