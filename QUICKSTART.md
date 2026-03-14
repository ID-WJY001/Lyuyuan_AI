# 快速启动和测试指南

## 当前配置

- **默认端口**: 8080
- **可通过环境变量修改**: `PORT=5000`

## 第一步：激活虚拟环境

### Windows PowerShell
```powershell
# 如果使用web_venv
.\web_venv\Scripts\Activate.ps1

# 如果使用.venv
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS
```bash
# 如果使用web_venv
source web_venv/bin/activate

# 如果使用.venv
source .venv/bin/activate
```

**验证虚拟环境已激活**:
- 命令行前面应该显示 `(web_venv)` 或 `(.venv)`
- 运行 `which python` (Linux/Mac) 或 `where python` (Windows) 应该指向虚拟环境

## 第二步：安装依赖（如果还没安装）

```bash
pip install -r requirements.txt
```

## 第三步：配置环境变量

确保 `.env` 文件存在并包含：
```
DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"
PORT=8080
```

## 第四步：启动服务器

```bash
python web_start.py
```

**预期输出**:
```
==================================================
正在启动 '绿园中学物语' Web版本...
==================================================
2026-03-14 16:00:00 - root - INFO - 当前工作目录已设置为: C:\Users\lenovo\Desktop\Lyuyuan_AI
2026-03-14 16:00:00 - root - INFO - 检测到.env文件，正在加载环境变量...
2026-03-14 16:00:00 - root - INFO - 成功从.env文件加载API密钥: sk-xx...xxxx
2026-03-14 16:00:00 - root - INFO - 确保目录 'saves' 已存在。
2026-03-14 16:00:00 - root - INFO - Web应用模块导入成功。
2026-03-14 16:00:00 - root - INFO - 正在启动Web服务器，请在浏览器中访问 http://127.0.0.1:8080
 * Serving Flask app 'app'
 * Running on http://0.0.0.0:8080
```

## 第五步：运行测试

**打开新的终端窗口**（保持服务器运行），然后：

### 1. 激活虚拟环境
```bash
# Windows
.\web_venv\Scripts\Activate.ps1

# Linux/Mac
source web_venv/bin/activate
```

### 2. 运行自动化测试
```bash
python tests/api_test.py
```

**预期输出**:
```
==================================================
  Lyuyuan AI API 自动化测试
==================================================
  测试服务器: http://localhost:8080
==================================================

检查服务器状态...
✓ 服务器正在运行

开始测试...

测试: 开始游戏(苏糖) ... ✓ PASSED (Status: 200)
测试: 开始游戏(林雨含) ... ✓ PASSED (Status: 200)
...
```

## 第六步：手动测试

打开浏览器访问：
```
http://localhost:8080
```

## 常见问题

### 1. 端口被占用

**错误**: `Address already in use`

**解决方案**:
```bash
# 方法1: 修改端口
# 在 .env 文件中添加或修改:
PORT=5000

# 方法2: 查找并关闭占用端口的进程
# Windows
netstat -ano | findstr :8080
taskkill /PID <进程ID> /F

# Linux/Mac
lsof -i :8080
kill -9 <进程ID>
```

### 2. 虚拟环境未激活

**错误**: `ModuleNotFoundError: No module named 'requests'`

**解决方案**:
```bash
# 确保激活虚拟环境
# Windows
.\web_venv\Scripts\Activate.ps1

# Linux/Mac
source web_venv/bin/activate

# 验证
python -c "import sys; print(sys.prefix)"
# 应该显示虚拟环境路径
```

### 3. API密钥未配置

**错误**: 对话时返回错误

**解决方案**:
```bash
# 检查 .env 文件
cat .env

# 确保包含:
DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"

# 重启服务器
```

### 4. 测试连接失败

**错误**: `无法连接到服务器`

**解决方案**:
1. 确保服务器正在运行
2. 检查端口是否正确（默认8080）
3. 尝试访问 `http://localhost:8080` 确认服务器可访问

## 快速命令参考

```bash
# 激活虚拟环境
.\web_venv\Scripts\Activate.ps1  # Windows
source web_venv/bin/activate     # Linux/Mac

# 启动服务器
python web_start.py

# 运行测试（新终端）
python tests/api_test.py

# 查看端口配置
cat .env | grep PORT

# 检查服务器是否运行
curl http://localhost:8080

# 停止服务器
# 在服务器终端按 Ctrl+C
```

## 测试端口配置

如果你想使用不同的端口：

### 方法1: 修改 .env 文件
```bash
# 编辑 .env
PORT=5000

# 重启服务器
python web_start.py
```

### 方法2: 临时设置环境变量
```bash
# Windows PowerShell
$env:PORT=5000
python web_start.py

# Linux/Mac
PORT=5000 python web_start.py
```

### 方法3: 修改测试脚本
```bash
# 运行测试时指定端口
PORT=5000 python tests/api_test.py
```

---

**提示**: 始终在虚拟环境中运行，避免依赖冲突！
