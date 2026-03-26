<img width="1583" height="796" alt="image" src="https://github.com/user-attachments/assets/ea713c3b-f8b5-46e1-b403-7b1bccbe0416" /># Flightclaw

**国内低价出行预规划 Skill**：用脚本拉取 **航班**（可接携程列表）与 **12306 列车**，支持 **直飞 / 中转 / 空铁联运** 思路；输出以 **时间轴 + 价格分项** 为准则（见根目录 [`SKILL.md`](SKILL.md)）。**不含订票、占座或支付**，数据均为检索页展示信息，以各平台下单页为准。

---

## 简介

**背景说明**：很多时候在购买机票时，**直飞未必比去周边大机场更便宜**——枢纽机场班次多、竞争强，票价有时明显低于本地小机场；再加上高铁/大巴衔接，总成本与总时间需要一起算。本仓库面向的正是这类「多出发地、多方式」的预规划与对比，而不是只看单一航线报价。

| 维度 | 说明 |
|------|------|
| **解决什么问题** | Agent 或脚本需要 **结构化（尤其 JSON）** 的国内机票/高铁检索结果，并在此基础上做 **多方案对比**（含枢纽周边、空铁衔接），而不是零散报价。 |
| **核心能力** | 机票：`flightclaw` Provider（`example` 占位、`ctrip` 携程 Playwright）；铁路：`12306-skill` 的 Node 脚本。 |
| **设计取向** | 强调 **总成本、总时间、衔接风险** 一起权衡；铁路注意 **约 15 天预售期**；携程检索可配合本机 Cookie 降低风控概率。 |
| **不适用** | 仅想随手打开网页订票；或需要 **自动化下单** —— 请使用官方 App/网站。 |

---

## 仓库结构

| 路径 | 说明 |
|------|------|
| **[`SKILL.md`](SKILL.md)** | **规范入口**（何时用、输出规范、Cookie 提示、命令摘要）— **发布时务必一并提供** |
| **[`docs/reference.md`](docs/reference.md)** | JSON、环境变量、扩展 Provider |
| **[`docs/examples.md`](docs/examples.md)** | 更多命令片段 |
| [`skills/flightclaw-skill/`](skills/flightclaw-skill/) | **机票** Python 包（`pyproject.toml`、`flightclaw/`、`tests/`） |
| [`skills/flightclaw-skill/flightclaw/skills/SKILL.md`](skills/flightclaw-skill/flightclaw/skills/SKILL.md) | 机票子包 **自包含** 说明（复制单技能目录时读此文件） |
| [`skills/12306-skill/`](skills/12306-skill/) | **铁路** 脚本（需 Node.js） |
| [`skills/openclaw-import/`](skills/openclaw-import/) | 方法论摘录与索引（**可选阅读**，非运行依赖） |

---

## 发布与接入（给使用方）

1. **整仓使用**：克隆本仓库；让 Agent 阅读根目录 [`SKILL.md`](SKILL.md)，并按其中安装命令安装 `flightclaw-skill` 与（可选）Playwright、Node。
2. **只发布「机票技能」子包**：使用 [`skills/flightclaw-skill/`](skills/flightclaw-skill/) 目录；其内 [`flightclaw/skills/SKILL.md`](skills/flightclaw-skill/flightclaw/skills/SKILL.md) 可独立说明用法。
3. **只发布「铁路技能」**：使用 [`skills/12306-skill/`](skills/12306-skill/) 及其中 `SKILL.md`。
4. **根目录 `SKILL.md` 的 YAML frontmatter**（`name` / `description`）可被 Cursor、Codex 等识别为 Agent Skill；描述中已标明携程 Cookie 变量名，避免误将密钥提交仓库。

**依赖摘要**：机票 — Python ≥ 3.9；携程 — `pip install -e ".[ctrip]"` 与 `playwright install chromium`；铁路 — Node.js（脚本无 `package.json`，**不需要** `npm install`）。

---

## 安装各技能

### 机票技能（`skills/flightclaw-skill`）

在**本仓库**中从该目录可编辑安装（含开发依赖与携程 Playwright 依赖）：

```bash
cd skills/flightclaw-skill
pip install -e ".[dev,ctrip]"
playwright install chromium
flightclaw --json today
```

- **仅验证 CLI / 占位检索**：可用 `pip install -e ".[dev]"` 或 `pip install -e .`，并用 `--provider example`（不装 Chromium、不访问携程）。
- **不执行 `pip install` 时**：在**仓库根目录**用 `PYTHONPATH` 已由 `scripts/flight.py` 处理，可直接：

```bash
python skills/flightclaw-skill/scripts/flight.py --json today
```

### 铁路技能（`skills/12306-skill`）

- 安装 **Node.js**（建议 **18+**，脚本为 ESM、使用原生 `fetch`）即可。
- **无需** 在该目录运行 `npm install`；用绝对路径或先 `cd` 到仓库根再调用：

```bash
node skills/12306-skill/scripts/query.mjs 北京 上海 -f md
```

### 整仓一起用（机票 + 铁路）

按上两节分别装好 **Python 环境 + Node** 后，Agent 阅读根目录 [`SKILL.md`](SKILL.md) 即可按规范串联 `flightclaw` 与 `query.mjs`。

### Agent / Cursor 技能接入

将本仓库 **根目录 [`SKILL.md`](SKILL.md)** 提供给 Agent（或复制到 Cursor `skills` 等目录）；其中 YAML `name` / `description` 可被识别为技能元数据。子目录内另有机票 [`flightclaw/skills/SKILL.md`](skills/flightclaw-skill/flightclaw/skills/SKILL.md)、铁路 [`12306-skill/SKILL.md`](skills/12306-skill/SKILL.md) 可单独分发。

---

## 案例

### 1. 占位航班检索（不联网，适合打通 CLI）

用于验证安装与 JSON 管道，不访问携程。

```bash
python skills/flightclaw-skill/scripts/flight.py --json search \
  --from BJS --to SHA --date 2026-04-01 --provider example
```

### 2. 携程真实列表（需 Playwright；Cookie 可选）

检索页展示价，**建议**配置本机 Cookie 文件路径（勿提交 Git）：

```bash
export FLIGHTCLAW_CTRIP_COOKIES_FILE="/本机路径/ctrip-cookies.json"   # 可选

flightclaw --json search --from WUX --to LJG --date 2026-03-28 --provider ctrip
```

### 3. 空铁联运思路（两工具配合）

先用 12306 看 **小城/高铁站 → 枢纽**，再用 `flightclaw` 查 **枢纽机场（IATA）→ 目的地**。示例：查某日 G 车与上海虹桥相关车次表（需按实际预售期改日期）：

```bash
node skills/12306-skill/scripts/query.mjs 无锡 上海虹桥 -d 2026-03-26 -t G -f md
```

再查 **上海** 出发航班（`SHA` 在系统中常对应上海两场，以 Provider 与页面为准）：

```bash
flightclaw --json search --from SHA --to LJG --date 2026-03-28 --provider ctrip
```

将 **二等座票价 + 市内接驳时间** 与 **直飞/经停方案** 放在同一表格里对比（详见 [`SKILL.md`](SKILL.md) 输出规范）。

### 4. REPL

```bash
flightclaw
# flightclaw> search --from BJS --to SHA --date 2026-04-01 --provider example
```

更多示例见 [`docs/examples.md`](docs/examples.md)。

---
<img width="1583" height="796" alt="image" src="https://github.com/user-attachments/assets/8bd75911-020a-4003-bbb2-ae98f60b8e4c" />
cookie使用cookie_editor导出到本地把保存地址发给opencalw即可
## 合规与免责声明

仅用于个人学习与研究。须遵守各平台服务条款与适用法律。查询结果不构成交易要约。
