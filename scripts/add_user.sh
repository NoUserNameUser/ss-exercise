#!/usr/bin/env bash
# 用法: ./add_user.sh <port> <password>
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/common.sh"

PORT="${1:?port required}"
PASS="${2:?password required}"

# 获取ss-manager的IP地址
MANAGER_IP=$(get_manager_ip)

# 1) ss-manager 动态添加端口
echo "add: {\"server_port\": ${PORT}, \"password\": \"${PASS}\"}" \
  | socat - UDP:${MANAGER_IP}:${MANAGER_PORT}
echo "[OK] ss-manager add port ${PORT}"

# 2) iptables 并发=1 规则（IPv4 示例；如果需要 IPv6，可再加 ip6tables）
# 说明：
# - TCP：限制新建连接（SYN）超过 1 条则拒绝（RST 更友好）
# - UDP：没有握手，按 conntrack 项限制超过 1 条则丢弃
# 注意：在 WSL2 等环境中，connlimit 模块可能不可用，使用 conntrack 作为替代
if iptables -C INPUT -p tcp --syn --dport ${PORT} -m connlimit --connlimit-above 1 -j REJECT --reject-with tcp-reset 2>/dev/null || iptables -I INPUT -p tcp --syn --dport ${PORT} -m connlimit --connlimit-above 1 -j REJECT --reject-with tcp-reset 2>/dev/null; then
    echo "[OK] connlimit rule added for TCP port ${PORT}"
else
    echo "[WARN] connlimit not available, using conntrack as fallback"
    add_rule_once "INPUT -p tcp --syn --dport ${PORT} -m conntrack --ctstate NEW -m limit --limit 1/sec -j ACCEPT"
    add_rule_once "INPUT -p tcp --syn --dport ${PORT} -j REJECT --reject-with tcp-reset"
fi

if iptables -C INPUT -p udp --dport ${PORT} -m connlimit --connlimit-above 1 -j DROP 2>/dev/null || iptables -I INPUT -p udp --dport ${PORT} -m connlimit --connlimit-above 1 -j DROP 2>/dev/null; then
    echo "[OK] connlimit rule added for UDP port ${PORT}"
else
    echo "[WARN] connlimit not available, using conntrack as fallback"
    add_rule_once "INPUT -p udp --dport ${PORT} -m conntrack --ctstate NEW -m limit --limit 1/sec -j ACCEPT"
    add_rule_once "INPUT -p udp --dport ${PORT} -j DROP"
fi

echo "[OK] connection limiting applied on port ${PORT} (tcp/udp)"
