#!/usr/bin/env python3
"""从仓库根目录调用时无需 pip 安装：将本技能根目录加入 PYTHONPATH 并启动 CLI。"""

from __future__ import annotations

import sys
from pathlib import Path

_SKILL_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    root = str(_SKILL_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    sys.argv[0] = "flightclaw"
    from flightclaw.flightclaw_cli import cli

    cli()


if __name__ == "__main__":
    main()
