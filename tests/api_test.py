"""
API自动化测试脚本 (Python版本)
适用于Windows/macOS/Linux
"""
import sys
import os

# 检查是否在虚拟环境中
def check_environment():
    """检查Python环境"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    if not in_venv:
        print("警告: 你似乎不在虚拟环境中运行")
        print("建议先激活虚拟环境:")
        print("  Windows: .\\web_venv\\Scripts\\Activate.ps1")
        print("  Linux/Mac: source web_venv/bin/activate")
        print()
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)

check_environment()

try:
    import requests
except ImportError:
    print("错误: 缺少 requests 模块")
    print("请安装: pip install requests")
    sys.exit(1)

import json
from typing import Dict, Any

# 从环境变量或配置文件读取端口
PORT = os.environ.get("PORT", "8080")
BASE_URL = f"http://localhost:{PORT}"

# 颜色代码（Windows可能不支持，但不影响功能）
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

passed = 0
failed = 0


def test_api(test_name: str, method: str, endpoint: str,
             data: Dict[str, Any] = None, expected_status: int = 200) -> bool:
    """测试API端点"""
    global passed, failed

    print(f"测试: {test_name} ... ", end="", flush=True)

    try:
        url = f"{BASE_URL}{endpoint}"

        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"{RED}✗ FAILED{NC} (不支持的方法: {method})")
            failed += 1
            return False

        if response.status_code == expected_status:
            print(f"{GREEN}✓ PASSED{NC} (Status: {response.status_code})")
            passed += 1
            return True
        else:
            print(f"{RED}✗ FAILED{NC} (Expected: {expected_status}, Got: {response.status_code})")
            print(f"  Response: {response.text[:200]}")
            failed += 1
            return False

    except requests.exceptions.ConnectionError:
        print(f"{RED}✗ FAILED{NC} (无法连接到服务器)")
        failed += 1
        return False
    except Exception as e:
        print(f"{RED}✗ FAILED{NC} (错误: {e})")
        failed += 1
        return False


def main():
    """主测试函数"""
    print("=" * 50)
    print("  Lyuyuan AI API 自动化测试")
    print("=" * 50)
    print(f"  测试服务器: {BASE_URL}")
    print("=" * 50)
    print()

    # 检查服务器是否运行
    print("检查服务器状态...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"{GREEN}✓ 服务器正在运行{NC}\n")
    except:
        print(f"{RED}✗ 无法连接到服务器 ({BASE_URL}){NC}")
        print("请确保服务器已启动: python web_start.py")
        sys.exit(1)

    print("开始测试...\n")

    # 测试1-5: 开始游戏 - 所有角色
    test_api("开始游戏(苏糖)", "POST", "/api/start_game", {"role": "su_tang"}, 200)
    test_api("开始游戏(林雨含)", "POST", "/api/start_game", {"role": "lin_yuhan"}, 200)
    test_api("开始游戏(罗一莫)", "POST", "/api/start_game", {"role": "luo_yimo"}, 200)
    test_api("开始游戏(顾盼)", "POST", "/api/start_game", {"role": "gu_pan"}, 200)
    test_api("开始游戏(夏星晚)", "POST", "/api/start_game", {"role": "xia_xingwan"}, 200)

    # 测试6: 列出存档
    test_api("列出存档", "GET", "/api/saves", None, 200)

    # 测试7: 空消息错误
    test_api("空消息错误", "POST", "/api/chat", {"message": ""}, 400)

    # 测试8: 缺少message字段
    test_api("缺少message字段", "POST", "/api/chat", {}, 400)

    # 打印结果
    print()
    print("=" * 50)
    print("  测试结果")
    print("=" * 50)
    print(f"{GREEN}通过: {passed}{NC}")
    print(f"{RED}失败: {failed}{NC}")
    print(f"总计: {passed + failed}")
    print()

    if failed == 0:
        print(f"{GREEN}所有测试通过！{NC}")
        sys.exit(0)
    else:
        print(f"{RED}有测试失败！{NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
