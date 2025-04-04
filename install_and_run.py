#!/usr/bin/env python
"""
绿园中学物语一键式安装和运行脚本
简化用户的初始化和启动体验
"""

import os
import sys

# 调整系统路径以解决可能的导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 尝试导入启动器脚本
try:
    from scripts.installation.launcher import main
    
    if __name__ == "__main__":
        # 运行启动器主函数
        main()
        
except ImportError:
    # 如果无法导入，可能是初次安装或路径问题
    # 尝试直接运行启动器脚本
    launcher_path = os.path.join(current_dir, "scripts", "installation", "launcher.py")
    
    if os.path.exists(launcher_path):
        print("正在运行启动器脚本...")
        with open(launcher_path, 'r', encoding='utf-8') as f:
            launcher_code = f.read()
            
        # 动态执行启动器脚本代码
        exec(launcher_code)
    else:
        print("错误: 找不到启动器脚本。请确保项目文件完整。")
        print(f"尝试查找的路径: {launcher_path}")
        sys.exit(1) 