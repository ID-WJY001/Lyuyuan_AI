from __future__ import annotations

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 提示词目录（默认在项目根的 prompts/，可通过环境变量覆盖）
PROMPTS_DIR = Path(os.environ.get("PROMPTS_DIR", PROJECT_ROOT / "prompts")).resolve()
