# `flightclaw` Python 包

独立可安装包（与仓库内 `skills/flightclaw-skill/pyproject.toml` 对应）。

- **Click** 命令行；无子命令时进入 **REPL**
- 全局 **`--json`** 输出
- 入口：`flightclaw` 或 `python -m flightclaw`

## 命令

| 命令 | 说明 |
|------|------|
| `today` | 本机日期 `YYYY-MM-DD` |
| `search` | `--from` / `--to` / `--date` / `--provider` |
| `providers` | 已注册的 Provider 名称 |
| `session` | 上一次查询与结果（JSON 结构） |
| `repl` | 显式进入 REPL（与无参数运行等价） |

## Provider

| 名称 | 说明 |
|------|------|
| `example` | 占位数据 |
| `ctrip` | 携程国内列表：Playwright + DOM 解析（`pip install -e ".[ctrip]"`，`playwright install chromium`） |

## 开发

在 `providers/` 注册新站点；纯 HTTP 用 `utils/http.py`。
