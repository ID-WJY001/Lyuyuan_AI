"""
绿园中学物语：追女生模拟 - 游戏主入口。

这个模块作为命令行版本游戏的启动点，
它会调用 `game.main` 中的 `main()` 函数来开始游戏。
"""

# 简单的重定向入口，调用game包中的主函数
from game.main import main

if __name__ == "__main__":
    main()