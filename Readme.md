# README.md

## 📌 项目简介
本项目提供了一个 **Shadowsocks-libev + ss-manager + iptables 并发限制** 的全容器化方案，能够实现：

- 多用户管理（每个用户独立端口+密码）  
- 动态添加/删除用户（无需重启服务）  
- **限制用户只能同时一台设备在线**（通过 iptables `connlimit`）  
- 批量添加/删除用户（Makefile + CSV）  

适合自用或小规模多用户场景。

---

## 🗂 目录结构
```
your-folder/
├─ .dockerignore
├─ docker-compose.yml
├─ ss-config.json
├─ Makefile
├─ users.csv            # 批量用户文件（可选）
└─ scripts/
   ├─ add_user.sh
   ├─ remove_user.sh
   └─ common.sh
```

---

## 🚀 快速开始

### 1. 准备环境
- Linux 服务器（Ubuntu/Debian/CentOS/Rocky 等均可）  
- 已安装 `docker` 和 `docker-compose`  
- 服务器需要支持 `iptables connlimit` 模块（大部分内核默认有）  

### 2. 启动服务
```bash
docker compose up -d
# 或
make up
```

会启动两个容器：
- `ss-manager` → 负责 shadowsocks-libev 核心与用户端口管理  
- `ss-guard` → 提供 iptables + 脚本工具，用于并发限制和用户管理  

---

## 👥 用户管理

### 单个用户
添加：
```bash
make add USER_PORT=8388 USER_PASS='StrongPass123'
```
删除：
```bash
make del USER_PORT=8388
```

### 批量用户
生成模板：
```bash
make gen_csv
```
编辑 `users.csv` 文件，格式如下：
```
8388,userA-pass
8389,userB-pass
8390,userC-pass
```

批量添加：
```bash
make bulk_add BULK_FILE=users.csv
```

批量删除：
```bash
make bulk_del BULK_FILE=users.csv
```

---

## 📊 监控与调试

查看 ss-manager 流量统计：
```bash
make stats
```

查看当前 iptables 限制规则：
```bash
make ipt_list
```

批量清理规则（指定端口区间）：
```bash
make ipt_clear_range PORT_START=8388 PORT_END=8399
```

自检（测试添加/删除流程）：
```bash
make selftest
```

---

## 🔒 并发限制原理

- **TCP**：通过 `iptables -m connlimit`，限制 `--connlimit-above 1`，超过 1 条并发连接时拒绝（返回 RST）。  
- **UDP**：同样通过 connlimit 限制超过 1 个“conntrack 条目”时丢弃新请求。  
- 这样可以确保“同一账号（端口）**只能同时在线一个设备**”。  

---

## ⚠️ 注意事项
- 每个用户需要独立端口，才能精确做并发控制。  
- 默认只处理 IPv4，如需 IPv6，请在 `scripts/` 中额外添加 `ip6tables` 规则。  
- 建议不要把 `6001/udp` 管理端口暴露公网（目前映射了宿主机端口，建议改成 `network_mode: host` 并移除端口映射）。  
- 建议用户密码随机复杂，避免撞库或爆破。  

---

## ✅ TODO / 可扩展
- [ ] 增加 `ip6tables` 规则，支持 IPv6 用户  
- [ ] 自动统计并发连接 IP，扩展成“限制不同 IP 数量”  
- [ ] 提供 Web 管理界面（调用 Makefile 脚本）  

---

📌 **使用方法总结**：  
- **自用少量用户** → 用 `make add/del` 管理即可  
- **批量分配** → 先 `make gen_csv`，编辑 `users.csv`，再 `make bulk_add`  
- **限制并发** → 已自动启用（无需额外配置）  
