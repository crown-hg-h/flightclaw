---
name: flightclaw
description: Search China domestic flights via pluggable providers (example mock, Ctrip Playwright). Use when user asks about 机票/航班/飞机票/携程/IATA/比价/直飞/中转 and wants scriptable or JSON output.
metadata: {"openclaw":{"emoji":"✈️","requires":{"bins":["python3"]}}}
---

# Flightclaw 机票技能（本包内完整规范）

下文所述路径均以 **本技能根目录** 为准（即包含 `pyproject.toml`、`flightclaw/`、`scripts/`、`tests/` 的这一层目录）。复制本文件夹到任意位置后，用法不变，**不要求**同仓库内其他文件。

## 目录结构（本技能包内）

| 路径 | 说明 |
|------|------|
| `pyproject.toml` | 包名 `flightclaw`，依赖与入口脚本 |
| `flightclaw/` | Python 源码（CLI、Provider、`core/`、`utils/`） |
| `scripts/flight.py` | 免 `pip install` 时：将本技能根目录加入 `PYTHONPATH` 后启动 CLI |
| `tests/` | `pytest` 用例 |

## 安装

在本技能根目录执行：

```bash
pip install -e ".[dev,ctrip]"
playwright install chromium
```

仅需占位检索、不跑携程：

```bash
pip install -e .
```

**Python 版本**：≥ 3.9。

## 命令

```text
flightclaw [--json] today
flightclaw [--json] search --from <IATA> --to <IATA> --date YYYY-MM-DD [--provider example|ctrip]
flightclaw [--json] providers
flightclaw [--json] session
flightclaw [repl]          # 显式 REPL；无子命令时默认也进入 REPL
python -m flightclaw ...   # 与 flightclaw 等价
```

未安装包时，在本技能根目录下：

```bash
python scripts/flight.py --json today
python scripts/flight.py --json search --from BJS --to SHA --date 2026-04-01 --provider example
```

若从其他工作目录调用 `scripts/flight.py`，请保证当前环境能解析 `flightclaw` 包（通常应先 `cd` 到本技能根目录再执行，或已 `pip install -e .`）。

## `--json` 输出结构

成功时 stdout 为 JSON，主要字段：

- `provider`：字符串，当前 Provider 名。
- `query`：`origin`、`destination`、`date`（ISO 日期字符串）。
- `offers[]`：每条含 `flight_no`、`dep_time`、`arr_time`、`price`、`currency`、`note`、`raw`。
- `warnings[]`：字符串数组（免责声明、风控提示、懒加载说明等）。

`example` Provider 的 `price` 可为占位；`ctrip` 为页面展示起价，**以官网为准**。

## Provider

| 名称 | 说明 |
|------|------|
| `example` | 本地占位，不访问网络。 |
| `ctrip` | 携程国内列表：无头 Chromium + 页面 DOM 解析；需 `pip install` 时带 `[ctrip]` 并安装 Chromium。 |

### 携程相关环境变量（可选，勿将密钥提交版本库）

| 变量 | 含义 |
|------|------|
| `FLIGHTCLAW_CTRIP_STORAGE_STATE` | Playwright `storage_state` JSON 文件路径；与 Cookie 文件二选一时优先。 |
| `FLIGHTCLAW_CTRIP_COOKIES_FILE` | Cookie JSON：Playwright 列表格式，或 Chrome 扩展（如 EditThisCookie）导出（可含 `storeId` / `expirationDate`）。 |
| `FLIGHTCLAW_CTRIP_SCROLL_ROUNDS` | 列表懒加载滚屏轮数，默认约 `35`，上限 `60`。 |

## 扩展新站点

1. 在 `flightclaw/providers/` 下新增模块，实现 `BaseProvider.search()`。
2. 在 `flightclaw/providers/__init__.py` 的 `PROVIDERS` 中注册。
3. 可参考 `flightclaw/providers/template_provider.py`、`example.py`、`ctrip.py`。

HTTP 辅助见 `flightclaw/utils/http.py`。

## 开发与本包内测试

在本技能根目录：

```bash
pytest
```

## 何时使用本技能

用户需要 **脚本化查国内航班**、**JSON 结果**、**携程列表起价参考**、或 **可插拔抓取** 时使用。

**触发示例（非穷尽）**：机票、航班、携程、IATA 三字码、比价、直飞、中转、`--json` 输出。

## 何时不使用

- 需要 **官方订票、占座、支付**：使用航司或 OTA 官网。
- 仅需 **人工浏览网页**：直接打开携程等站点。

## 与行程规划协作时的输出格式（本仓库）

若与 **12306**、多枢纽比价、空铁联运等一并输出给用户，**多方案 Markdown 总表 + 推荐行加粗** 的约定见 **仓库根目录** [`SKILL.md`](../../../../SKILL.md) 中 **「Agent 最终输出规范」→ 第 3 节「多方案汇总表（推荐格式）」**。

## 合规与免责声明

仅供个人学习与技术验证。使用 `ctrip` 时须自行遵守 **https://www.ctrip.com** 用户协议、robots.txt 及适用法律。输出 **不构成** 交易要约；票价与余票以官网为准。
