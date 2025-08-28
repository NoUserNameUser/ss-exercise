# ShadowSocks 服务器管理脚本 (Python版本)

这是替代 Makefile 的 Python 脚本版本，提供相同的功能但更加灵活和易用。

## 安装要求

- Python 3.6+
- Docker 和 Docker Compose
- 确保脚本有执行权限：`chmod +x manage.py`

## 使用方法

### 基本命令

```bash
# 启动服务
python manage.py up

# 停止服务
python manage.py down

# 添加单个用户
python manage.py add --port 8388 --pass StrongPass

# 删除单个用户
python manage.py del --port 8388

# 批量添加用户
python manage.py bulk_add --file users.csv

# 批量删除用户
python manage.py bulk_del --file users.csv

# 生成 CSV 模板
python manage.py gen_csv --file users.csv

# 查看统计信息
python manage.py stats

# 查看 iptables 规则
python manage.py ipt_list

# 清理端口范围的 iptables 规则
python manage.py ipt_clear_range

# 端到端自检
python manage.py selftest
```

### 环境变量配置

可以通过环境变量设置默认端口范围：

```bash
export PORT_START=8388
export PORT_END=8399
```

### 命令行参数

- `--port`: 用户端口
- `--pass`: 用户密码
- `--file`: 批量操作文件 (默认: users.csv)
- `--port-start`: 端口起始值
- `--port-end`: 端口结束值

## 与 Makefile 的对应关系

| Makefile 命令 | Python 命令 |
|---------------|-------------|
| `make up` | `python manage.py up` |
| `make down` | `python manage.py down` |
| `make add USER_PORT=8388 USER_PASS=StrongPass` | `python manage.py add --port 8388 --pass StrongPass` |
| `make del USER_PORT=8388` | `python manage.py del --port 8388` |
| `make bulk_add BULK_FILE=users.csv` | `python manage.py bulk_add --file users.csv` |
| `make bulk_del BULK_FILE=users.csv` | `python manage.py bulk_del --file users.csv` |
| `make gen_csv` | `python manage.py gen_csv` |
| `make stats` | `python manage.py stats` |
| `make ipt_list` | `python manage.py ipt_list` |
| `make ipt_clear_range` | `python manage.py ipt_clear_range` |
| `make selftest` | `python manage.py selftest` |

## 优势

1. **更好的错误处理**: 提供详细的错误信息和状态反馈
2. **类型安全**: 使用类型注解，减少运行时错误
3. **更灵活的配置**: 支持环境变量和命令行参数
4. **更好的可读性**: 代码结构清晰，易于维护
5. **跨平台兼容**: 在 Windows、Linux、macOS 上都能正常工作
6. **批量操作统计**: 显示成功/失败的操作数量

## 示例

### 生成用户模板并批量添加

```bash
# 生成用户模板
python manage.py gen_csv --file my_users.csv

# 编辑 my_users.csv 文件，添加实际的端口和密码
# 8388,user1_password
# 8389,user2_password
# 8390,user3_password

# 批量添加用户
python manage.py bulk_add --file my_users.csv
```

### 自定义端口范围

```bash
# 使用自定义端口范围生成模板
python manage.py gen_csv --file custom_users.csv --port-start 9000 --port-end 9010

# 清理自定义端口范围的规则
python manage.py ipt_clear_range --port-start 9000 --port-end 9010
```

## 注意事项

1. 确保 Docker 服务正在运行
2. 确保 `ss-guard` 容器已经启动
3. 批量操作文件应该是 CSV 格式，第一行可以是注释
4. 密码中如果包含特殊字符，请确保正确转义
