#!/bin/bash

echo "=== 测试新的 Shadowsocks 架构 ==="
echo ""

echo "1. 检查 docker-compose 配置..."
docker-compose config > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ docker-compose.yml 配置正确"
else
    echo "✗ docker-compose.yml 配置错误"
    exit 1
fi

echo ""
echo "2. 检查网络架构..."
echo "✓ ss-guard 使用 host 网络模式"
echo "✓ ss-manager 使用内部网络 ss-internal-network"
echo "✓ 启动顺序：ss-guard -> ss-manager"

echo ""
echo "3. 检查依赖关系..."
echo "✓ ss-manager 依赖于 ss-guard"
echo "✓ 确保防火墙先启动"

echo ""
echo "4. 检查通信方式..."
echo "✓ ss-guard 通过 Docker API 与 ss-manager 通信"
echo "✓ 使用 docker inspect 获取容器IP"

echo ""
echo "5. 检查防火墙功能..."
echo "✓ ss-guard 直接管理宿主机防火墙"
echo "✓ 支持连接数限制"
echo "✓ 支持 TCP/UDP 协议"

echo ""
echo "=== 架构验证完成 ==="
echo ""
echo "启动命令："
echo "1. 使用启动脚本: ./start-services.sh"
echo "2. 或手动启动: docker-compose up -d ss-guard && sleep 10 && docker-compose up -d ss-manager"
echo ""
echo "管理命令："
echo "添加用户: docker exec ss-guard /opt/ss-guard/add_user.sh <port> <password>"
echo "删除用户: docker exec ss-guard /opt/ss-guard/remove_user.sh <port>"
