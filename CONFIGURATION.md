# Shadowsocks Docker 配置说明

## 架构设计

本项目采用分层架构，确保防火墙在宿主机网络层，shadowsocks服务在内网运行：

### 容器结构
- **ss-guard**: 防火墙管理容器（宿主机网络）
  - 直接接入宿主机网络
  - 运行iptables防火墙
  - 管理用户连接限制
  - 通过Docker API与ss-manager通信
  
- **ss-manager**: Shadowsocks服务器容器（内网）
  - 运行ss-manager服务
  - 监听端口8388-8399 (TCP/UDP)
  - 管理端口6001 (UDP)
  - 在内部网络中运行

### 网络配置
- ss-guard使用host网络模式，直接管理宿主机防火墙
- ss-manager在ss-internal-network内部网络中运行
- 通过Docker API实现容器间通信

## 主要修改

### 1. 网络架构修改
```yaml
# ss-guard 使用宿主机网络
ss-guard:
  network_mode: host

# ss-manager 使用内部网络
ss-manager:
  networks:
    - ss-internal-network
```

### 2. 启动顺序调整
```yaml
# ss-manager 依赖于 ss-guard
ss-manager:
  depends_on:
    - ss-guard
```

### 3. 通信方式修改
```bash
# 通过Docker API获取容器IP
get_manager_ip() {
    docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $MANAGER_CONTAINER
}
```

## 优势

1. **防火墙控制**: ss-guard直接管理宿主机防火墙，更有效
2. **网络隔离**: ss-manager在内网运行，提高安全性
3. **启动顺序**: 先启动防火墙，再启动服务
4. **易于管理**: 可以独立管理防火墙和服务

## 使用方法

### 启动服务（推荐使用启动脚本）
```bash
# 使用启动脚本确保正确顺序
./start-services.sh

# 或手动启动
docker-compose up -d ss-guard
sleep 10
docker-compose up -d ss-manager
```

### 添加用户
```bash
docker exec ss-guard /opt/ss-guard/add_user.sh <port> <password>
```

### 删除用户
```bash
docker exec ss-guard /opt/ss-guard/remove_user.sh <port>
```

### 查看日志
```bash
# 查看ss-guard日志
docker logs ss-guard

# 查看ss-manager日志
docker logs ss-manager
```

## 防火墙功能

ss-guard容器提供以下防火墙功能：
- 每个端口限制并发连接数为1
- 支持TCP和UDP协议
- 自动添加和删除防火墙规则
- 使用connlimit模块或conntrack作为备选方案
- 直接管理宿主机防火墙规则
