#!/usr/bin/env bash
set -euo pipefail

# 统一的变量与工具函数
MANAGER_CONTAINER="ss-manager"
MANAGER_PORT="6001"

# 检查 iptables 可用性
command -v iptables >/dev/null || { echo "[ERR] iptables not found"; exit 1; }

# 一些发行版默认启用 nft 后端；我们尽量用当前系统默认的 iptables 命令即可。
# 如需强制 legacy，可把 iptables 替换为 iptables-legacy。
IPT="iptables"

# 获取ss-manager容器的IP地址
get_manager_ip() {
    docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $MANAGER_CONTAINER 2>/dev/null || echo "127.0.0.1"
}

# 幂等添加规则：如果规则已存在就不重复添加
add_rule_once() {
  local rule="$1"
  # 用 -C 检查是否存在（存在则返回 0）
  if $IPT -C $rule 2>/dev/null; then
    echo "[SKIP] rule exists: $rule"
  else
    $IPT -I $rule
    echo "[OK] added: $rule"
  fi
}

# 幂等删除规则：不存在就忽略
del_rule_if_present() {
  local rule="$1"
  if $IPT -C $rule 2>/dev/null; then
    $IPT -D $rule || true
    echo "[OK] deleted: $rule"
  else
    echo "[SKIP] not found: $rule"
  fi
}
