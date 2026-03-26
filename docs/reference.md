# Flightclaw — 参考手册

**定位**：与根目录 [`SKILL.md`](../SKILL.md) **并列的速查页**（命令、JSON 字段、环境变量）；**方法论、Agent 输出规范、多枢纽检索清单** 以 **`SKILL.md` 为准**。

总览见仓库根目录 [`SKILL.md`](../SKILL.md)（含 **「Agent 检索清单（可选）」** 等）。

## 机票独立技能包

与 **[`skills/12306-skill/`](../skills/12306-skill/)** 并列：**[`skills/flightclaw-skill/`](../skills/flightclaw-skill/)** 为 **自包含** Python 项目（`pyproject.toml`、`flightclaw/`、`tests/`）。

```bash
cd skills/flightclaw-skill   # 本目录下安装
pip install -e ".[dev,ctrip]"
playwright install chromium
```

在仓库根目录、**未安装** 时可直接：

```bash
python skills/flightclaw-skill/scripts/flight.py --json today
python skills/flightclaw-skill/scripts/flight.py --json search --from BJS --to SHA --date 2026-04-01 --provider example
```

`scripts/flight.py` 将 `skills/flightclaw-skill` 加入 `PYTHONPATH`，与 `flightclaw` / `python -m flightclaw` 行为一致。

## 命令

```text
flightclaw [--json] today
flightclaw [--json] search --from BJS --to LJG --date YYYY-MM-DD [--provider example|ctrip]
flightclaw [--json] providers
flightclaw [--json] session
flightclaw [repl]          # 无参数 = REPL
python -m flightclaw ...
```

## `search` 输出 JSON 结构

- `provider`：Provider 名称  
- `query`：`origin`、`destination`、`date`  
- `offers[]`：`flight_no`、`dep_time`、`arr_time`、`price`、`currency`、`note`、`raw`  
- `warnings[]`：免责声明、Cookie 使用提示、懒加载说明等  

`example` Provider 的 `price` 可能为占位；`ctrip` 为页面展示起价，**以官网为准**。

## 携程 Provider（`--provider ctrip`）

- 使用 **Playwright** 无头 Chromium，解析列表页 DOM；须自行遵守携程用户协议。
- **会话 / Cookie（推荐）**：遇风控、海外 IP 或需登录态时，设置环境变量（**勿提交仓库**）：
  - `FLIGHTCLAW_CTRIP_STORAGE_STATE`：Playwright 导出的 `storage_state` JSON 路径（与下项二选一，优先）。
  - `FLIGHTCLAW_CTRIP_COOKIES_FILE`：Cookie JSON 路径。支持 **Playwright 列表**或 **Chrome 扩展导出**（EditThisCookie 等，含 `storeId` / `expirationDate`），会自动转换。
- **懒加载**：列表随滚动加载更多直飞/中转。脚本会自动多次 `End` 滚屏。可调 `FLIGHTCLAW_CTRIP_SCROLL_ROUNDS`（默认约 35，上限 60）。

## 12306 铁路（OpenClaw 同源技能）

本仓库包含 **[`skills/12306-skill/`](../skills/12306-skill/)**（由本机 `~/.openclaw/workspace/skills/12306-skill` 拷贝，不含嵌套 `.git`）。规范见该目录下的 [`SKILL.md`](../skills/12306-skill/SKILL.md)。

- **依赖**：系统已安装 **Node.js**（`metadata.openclaw.requires.bins` 为 `node`）。
- **路径约定**：文档中的 `{baseDir}` 在 flightclaw 仓库内即 **仓库根目录**，脚本为 `skills/12306-skill/scripts/query.mjs`、`stations.mjs`。
- **缓存**：首次运行会从 12306 拉取车站数据，写入 `skills/12306-skill/data/stations.json`（该文件在技能 `.gitignore` 中，**不提交**；本地拷贝若已有缓存可继续使用）。
- **预售期**：仅可查预售期内日期（常见约 **15 天**，以 12306 为准）。**Agent 流程**：先取当天日期；若用户乘车日 **超出预售**，对 `query.mjs` 使用 **当天 + 10 天** 作为参考日查 **G/D 班次与价位**（运行图通常日日复用），并在输出中标明「参考日 ≠ 出行日」。详见根目录 [`SKILL.md`](../SKILL.md) 与 [`skills/12306-skill/SKILL.md`](../skills/12306-skill/SKILL.md)。可选方法论摘录见 [`skills/openclaw-import/`](../skills/openclaw-import/)（若仓库中包含该目录；非运行依赖）。

## 扩展新站点

复制 [`skills/flightclaw-skill/flightclaw/providers/template_provider.py`](../skills/flightclaw-skill/flightclaw/providers/template_provider.py)，实现 `search()`，在 [`providers/__init__.py`](../skills/flightclaw-skill/flightclaw/providers/__init__.py) 的 `PROVIDERS` 中注册。
