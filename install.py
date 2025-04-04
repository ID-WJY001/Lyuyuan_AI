#!/usr/bin/env python
"""
绿园中学物语安装脚本
主安装脚本，用于安装游戏必要的依赖和配置
"""

import os
import sys

# 调整系统路径以解决可能的导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 尝试导入安装脚本
try:
    from scripts.installation.installer import main
    
    if __name__ == "__main__":
        # 运行安装主函数
        main()
        
except ImportError:
    # 如果无法导入，可能是初次安装或路径问题
    # 尝试直接运行安装脚本
    installer_path = os.path.join(current_dir, "scripts", "installation", "installer.py")
    
    if os.path.exists(installer_path):
        print("正在运行安装脚本...")
        with open(installer_path, 'r', encoding='utf-8') as f:
            installer_code = f.read()
            
        # 动态执行安装脚本代码
        exec(installer_code)
    else:
        print("错误: 找不到安装脚本。请确保项目文件完整。")
        print(f"尝试查找的路径: {installer_path}")
        sys.exit(1) 