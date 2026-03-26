---
name: flightclaw
description: Search China domestic flights via pluggable providers (example mock, Ctrip Playwright). Use when user asks about 机票/航班/飞机票/携程/IATA/比价/直飞/中转 and wants scriptable or JSON output.
metadata: {"openclaw":{"emoji":"✈️","requires":{"bins":["python3"]}}}
---

# Flightclaw 机票 Skill

**完整、自包含的规范与用法**（不依赖本文件夹外的文档）见：

**[`flightclaw/skills/SKILL.md`](flightclaw/skills/SKILL.md)**

以下为快速入口。

## 安装（在本技能根目录）

```bash
pip install -e ".[dev,ctrip]"
playwright install chromium
```

## 快速命令

```bash
flightclaw --json today
flightclaw --json search --from BJS --to SHA --date 2026-04-01 --provider example
```

未安装时：`python scripts/flight.py --json today`（在本技能根目录执行）。

更多说明、JSON 结构、环境变量、扩展 Provider、合规条款，一律以 **`flightclaw/skills/SKILL.md`** 为准。
