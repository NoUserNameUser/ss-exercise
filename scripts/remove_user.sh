#!/usr/bin/env bash
# 用法: ./remove_user.sh <port>
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/common.sh"

PORT="${1:?port required}"

# 获取ss-manager的IP地址
MANAGER_IP=$(get_manager_ip)

# 1) 删除 ss-manager 端口
echo "remove: {\"server_port\": ${PORT}}" \
  | socat - UDP:${MANAGER_IP}:${MANAGER_PORT}
echo "[OK] ss-manager remove port ${PORT}"

# 2) 移除 iptables 限制规则（与添加时完全一致以便精准删除）
# 尝试删除 connlimit 规则
del_rule_if_present "INPUT -p tcp --syn --dport ${PORT} -m connlimit --connlimit-above 1 -j REJECT --reject-with tcp-reset"
del_rule_if_present "INPUT -p udp --dport ${PORT} -m connlimit --connlimit-above 1 -j DROP"

# 尝试删除 conntrack 备用规则
del_rule_if_present "INPUT -p tcp --syn --dport ${PORT} -m conntrack --ctstate NEW -m limit --limit 1/sec -j ACCEPT"
del_rule_if_present "INPUT -p tcp --syn --dport ${PORT} -j REJECT --reject-with tcp-reset"
del_rule_if_present "INPUT -p udp --dport ${PORT} -m conntrack --ctstate NEW -m limit --limit 1/sec -j ACCEPT"
del_rule_if_present "INPUT -p udp --dport ${PORT} -j DROP"
