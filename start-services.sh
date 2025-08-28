#!/bin/bash

echo "=== 启动 Shadowsocks 服务 ==="
echo ""

echo "1. 启动 ss-guard 防火墙服务..."
docker-compose up -d ss-guard

echo "2. 等待 ss-guard 准备就绪..."
sleep 10

echo "3. 启动 ss-manager 服务..."
docker-compose up -d ss-manager

echo "4. 等待 ss-manager 启动完成..."
sleep 5

echo "5. 检查服务状态..."
docker ps --filter "name=ss-"

echo ""
echo "=== 服务启动完成 ==="
echo ""
echo "使用方法："
echo "添加用户: docker exec ss-guard /opt/ss-guard/add_user.sh <port> <password>"
echo "删除用户: docker exec ss-guard /opt/ss-guard/remove_user.sh <port>"
echo "查看日志: docker logs ss-guard 或 docker logs ss-manager"
