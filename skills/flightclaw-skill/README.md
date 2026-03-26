# Flightclaw 机票 Skill

自包含 Python 包：`pyproject.toml`、`flightclaw/`、`scripts/`、`tests/`。

**完整规范（仅依赖本文件夹内文档）**：[`flightclaw/skills/SKILL.md`](flightclaw/skills/SKILL.md)

## 安装

```bash
pip install -e ".[dev,ctrip]"
playwright install chromium
```

## 用法

```bash
flightclaw --json today
python -m flightclaw --json providers
```

免安装（在本技能根目录）：

```bash
python scripts/flight.py --json today
```

## 测试

```bash
pytest
```
