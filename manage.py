#!/usr/bin/env python3
"""
ShadowSocks 服务器管理脚本
替代 Makefile 的 Python 版本
"""

import argparse
import csv
import os
import subprocess
import sys
from typing import Optional, Tuple


class ShadowSocksManager:
    def __init__(self):
        # 默认端口区间（与 compose 的映射一致，批量时会用到）
        self.port_start = int(os.getenv('PORT_START', '8388'))
        self.port_end = int(os.getenv('PORT_END', '8399'))
        
    def run_docker_command(self, command: str, interactive: bool = False) -> bool:
        """执行 Docker 命令"""
        try:
            if interactive:
                subprocess.run(command, shell=True, check=True)
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
                if result.stdout:
                    print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERR] 命令执行失败: {e}")
            if e.stderr:
                print(f"错误信息: {e.stderr}")
            return False

    def up(self):
        """启动服务"""
        print("[INFO] 启动 ShadowSocks 服务...")
        return self.run_docker_command("docker compose up -d")

    def down(self):
        """停止服务"""
        print("[INFO] 停止 ShadowSocks 服务...")
        return self.run_docker_command("docker compose down")

    def add_user(self, port: str, password: str):
        """添加单个用户"""
        if not port or not password:
            print("[ERR] USER_PORT 和 USER_PASS 都是必需的")
            return False
        
        print(f"[INFO] 添加用户: 端口 {port}")
        command = f'docker exec -it ss-guard bash -lc "/opt/ss-guard/add_user.sh {port} \'{password}\'"'
        return self.run_docker_command(command, interactive=True)

    def del_user(self, port: str):
        """删除单个用户"""
        if not port:
            print("[ERR] USER_PORT 是必需的")
            return False
        
        print(f"[INFO] 删除用户: 端口 {port}")
        command = f'docker exec -it ss-guard bash -lc "/opt/ss-guard/remove_user.sh {port}"'
        return self.run_docker_command(command, interactive=True)

    def bulk_add(self, bulk_file: str):
        """批量添加用户"""
        if not os.path.exists(bulk_file):
            print(f"[ERR] 批量文件未找到: {bulk_file}")
            return False
        
        print(f"[INFO] 从 {bulk_file} 批量添加用户")
        success_count = 0
        total_count = 0
        
        try:
            with open(bulk_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2 and row[0].strip() and row[1].strip():
                        port, password = row[0].strip(), row[1].strip()
                        total_count += 1
                        print(f">> 添加 {port}")
                        if self.add_user(port, password):
                            success_count += 1
        except Exception as e:
            print(f"[ERR] 读取批量文件失败: {e}")
            return False
        
        print(f"[OK] 批量添加完成. 成功: {success_count}/{total_count}")
        return success_count == total_count

    def bulk_del(self, bulk_file: str):
        """批量删除用户"""
        if not os.path.exists(bulk_file):
            print(f"[ERR] 批量文件未找到: {bulk_file}")
            return False
        
        print(f"[INFO] 从 {bulk_file} 批量删除用户")
        success_count = 0
        total_count = 0
        
        try:
            with open(bulk_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 1 and row[0].strip():
                        port = row[0].strip()
                        total_count += 1
                        print(f">> 删除 {port}")
                        if self.del_user(port):
                            success_count += 1
        except Exception as e:
            print(f"[ERR] 读取批量文件失败: {e}")
            return False
        
        print(f"[OK] 批量删除完成. 成功: {success_count}/{total_count}")
        return success_count == total_count

    def gen_csv(self, filename: str = "users.csv"):
        """生成 CSV 模板文件"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["# port", "password"])
                for i in range(self.port_start, self.port_end + 1):
                    writer.writerow([str(i), f"password-{i}"])
            print(f"[OK] 已生成 {filename}")
            return True
        except Exception as e:
            print(f"[ERR] 生成 CSV 文件失败: {e}")
            return False

    def stats(self):
        """查看 ss-manager 统计"""
        print("[INFO] 查看 ss-manager 统计...")
        command = 'docker exec -it ss-guard bash -lc "echo \'stat: {}\' | socat - UDP:127.0.0.1:6001 || true"'
        return self.run_docker_command(command, interactive=True)

    def ipt_list(self):
        """查看 iptables 规则"""
        print("[INFO] 查看 iptables 规则...")
        command = 'docker exec -it ss-guard bash -lc "iptables -S | sed -n \'/--connlimit-above 1/p\'"'
        return self.run_docker_command(command, interactive=True)

    def ipt_clear_range(self):
        """清理指定端口范围的 iptables 规则"""
        print(f"[WARN] 将尝试删除端口范围 {self.port_start}-{self.port_end} 的 connlimit 规则")
        
        for i in range(self.port_start, self.port_end + 1):
            # 删除 TCP 规则
            tcp_cmd = f'docker exec -i ss-guard bash -lc "iptables -D INPUT -p tcp --syn --dport {i} -m connlimit --connlimit-above 1 -j REJECT --reject-with tcp-reset || true"'
            self.run_docker_command(tcp_cmd)
            
            # 删除 UDP 规则
            udp_cmd = f'docker exec -i ss-guard bash -lc "iptables -D INPUT -p udp --dport {i} -m connlimit --connlimit-above 1 -j DROP || true"'
            self.run_docker_command(udp_cmd)
        
        print("[OK] 已清理端口范围的规则")
        return True

    def selftest(self):
        """端到端自检"""
        print("[INFO] 开始端到端自检...")
        
        # 启动服务
        if not self.up():
            return False
        
        # 添加测试用户
        test_port = str(self.port_start)
        test_password = f"test-{test_port}"
        if not self.add_user(test_port, test_password):
            return False
        
        # 查看规则
        self.ipt_list()
        
        # 删除测试用户
        if not self.del_user(test_port):
            return False
        
        # 再次查看规则
        self.ipt_list()
        
        print("[OK] 自检完成")
        return True


def main():
    parser = argparse.ArgumentParser(description="ShadowSocks 服务器管理脚本")
    parser.add_argument('command', choices=[
        'up', 'down', 'add', 'del', 'bulk_add', 'bulk_del', 
        'gen_csv', 'stats', 'ipt_list', 'ipt_clear_range', 'selftest'
    ], help='要执行的命令')
    
    parser.add_argument('--port', dest='user_port', help='用户端口')
    parser.add_argument('--pass', dest='user_pass', help='用户密码')
    parser.add_argument('--file', dest='bulk_file', default='users.csv', help='批量操作文件')
    parser.add_argument('--port-start', type=int, help='端口起始值')
    parser.add_argument('--port-end', type=int, help='端口结束值')
    
    args = parser.parse_args()
    
    # 创建管理器实例
    manager = ShadowSocksManager()
    
    # 设置端口范围（如果提供）
    if args.port_start:
        manager.port_start = args.port_start
    if args.port_end:
        manager.port_end = args.port_end
    
    # 执行命令
    success = False
    
    if args.command == 'up':
        success = manager.up()
    elif args.command == 'down':
        success = manager.down()
    elif args.command == 'add':
        success = manager.add_user(args.user_port, args.user_pass)
    elif args.command == 'del':
        success = manager.del_user(args.user_port)
    elif args.command == 'bulk_add':
        success = manager.bulk_add(args.bulk_file)
    elif args.command == 'bulk_del':
        success = manager.bulk_del(args.bulk_file)
    elif args.command == 'gen_csv':
        success = manager.gen_csv(args.bulk_file)
    elif args.command == 'stats':
        success = manager.stats()
    elif args.command == 'ipt_list':
        success = manager.ipt_list()
    elif args.command == 'ipt_clear_range':
        success = manager.ipt_clear_range()
    elif args.command == 'selftest':
        success = manager.selftest()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
