---
name: "12306"
description: Query China Railway 12306 for train schedules, remaining tickets, and station info. Use when user asks about train/高铁/火车 tickets, schedules, or availability within China.
metadata: {"openclaw":{"emoji":"🚄","requires":{"bins":["node"]}}}
---

# 12306 Train Query

Query train schedules and remaining tickets from China Railway 12306.

## Query Tickets

```bash
node {baseDir}/scripts/query.mjs <from> <to> [options]
```

- HTML mode (default): writes file, prints path to stdout
- Markdown mode (`-f md`): prints table to stdout

### Examples

```bash
# All trains from Beijing to Shanghai (defaults to today)
node {baseDir}/scripts/query.mjs 北京 上海

# Markdown table output (to stdout, good for chat)
node {baseDir}/scripts/query.mjs 北京 上海 -t G -f md

# Morning departures, 2h max, with second class available
node {baseDir}/scripts/query.mjs 上海 杭州 -t G --depart 06:00-12:00 --max-duration 1h --seat ze

# Only bookable trains arriving before 6pm
node {baseDir}/scripts/query.mjs 深圳 长沙 --available --arrive -18:00

# Custom output path
node {baseDir}/scripts/query.mjs 广州 武汉 -o /tmp/tickets.html

# JSON output (to stdout)
node {baseDir}/scripts/query.mjs 广州 武汉 --json
```

### Options

- `-d, --date <YYYY-MM-DD>`: Travel date (default: today)
- `-t, --type <G|D|Z|T|K>`: Filter train types (combinable, e.g. `GD`)
- `--depart <HH:MM-HH:MM>`: Depart time range (e.g. `08:00-12:00`, `18:00-`)
- `--arrive <HH:MM-HH:MM>`: Arrive time range (e.g. `-18:00`, `14:00-20:00`)
- `--max-duration <duration>`: Max travel time (e.g. `2h`, `90m`, `1h30m`)
- `--available`: Only show bookable trains
- `--seat <types>`: Only show trains with tickets for given seat types (comma-separated: `swz,zy,ze,rw,dw,yw,yz,wz`)
- `-f, --format <html|md>`: Output format — `html` (default, saves file) or `md` (markdown table to stdout)
- `-o, --output <path>`: Output file path, html mode only (default: `{baseDir}/data/<from>-<to>-<date>.html`)
- `--json`: Output raw JSON to stdout

### Output Columns

| Column | Meaning |
|--------|---------|
| 商务/特等 | Business class / Premium (swz) |
| 一等座 | First class (zy) |
| 二等座 | Second class (ze) |
| 软卧/动卧 | Soft sleeper / Bullet sleeper (rw/dw) |
| 硬卧 | Hard sleeper (yw) |
| 硬座 | Hard seat (yz) |
| 无座 | Standing (wz) |

Values: number = remaining seats, `有` = available (qty unknown), `—` = not applicable

## Station Lookup

```bash
node {baseDir}/scripts/stations.mjs 杭州
node {baseDir}/scripts/stations.mjs 香港西九龙
```

## Important Notes for AI Assistant

### ⚠️ Station Name Resolution Warning

**CRITICAL**: When querying by city name (e.g., "武汉", "上海", "深圳", "广州"), the API may return trains from/to ANY station in that city, not just the main station.

**Common Pitfalls:**
- **武汉** includes: 武汉站 (main), 汉口站 (Hankou), 武昌站 (Wuchang), 武汉东站
- **上海** includes: 上海虹桥 (Hongqiao), 上海站 (main), 上海南站, 上海松江站
- **深圳** includes: 深圳北站 (main), 深圳站 (Luohu), 福田站, 深圳东站
- **广州** includes: 广州南站 (main), 广州站, 广州东站, 广州北站

**Best Practice - Always verify exact stations:**
1. **First**, use `stations.mjs` to list all stations in the city:
   ```bash
   node {baseDir}/scripts/stations.mjs 武汉
   ```
2. **Then**, query with exact station names for accurate results:
   ```bash
   node {baseDir}/scripts/query.mjs 武汉 上海虹桥 -f md
   ```

### 🔄 Transfer/Connection Guidelines

When planning transfers (中转):
- **Use JSON output** (`--json`) to verify exact station names
- Ensure both segments use the **SAME station** (e.g., both use 武汉站, not 武汉→汉口)
- Recommended minimum transfer time: **20-30 minutes** for same station
- **Different stations** in same city require additional travel time (e.g., 武汉→汉口 = 30+ min by subway)

### 📅 当天日期与「参考日」（Agent 必循）

1. **先取当天日期** `T`（`YYYY-MM-DD`）：可与机票检索一致，用仓库根目录 `flightclaw today`，或本机上海时区日期。
2. **用户目的乘车日** `D`：若 **`D` 距 `T` 超过约 15 天**（尚未进入常见预售窗口），**不要**指望对 `D` 查到可售余票；应改用 **参考日 `R = T + 10 天`** 调用 `query.mjs -d R`。
3. **含义**：高铁 **G/D** 等线路 **每日运行图通常固定**，用 **`R`** 查到的 **车次、时刻、耗时、二等座价位** 可作为 **远期出行日** 的 **规划参考**；输出时必须写明 **「查询日为参考日 R，非用户出行日 D」**，并以 **临近开售时 12306 实际 `D`** 为准。
4. 若 **`D` 已在预售期内**（距 `T` 约 ≤ 15 天）：**直接** `-d D` 查询。

### 📋 Query Workflow Recommendation

**For accurate results, follow this workflow:**

1. **List stations** in departure city:
   ```bash
   node {baseDir}/scripts/stations.mjs 北京
   ```

2. **List stations** in arrival city:
   ```bash
   node {baseDir}/scripts/stations.mjs 上海
   ```

3. **Query with exact station names** (e.g., 北京南 → 上海虹桥):
   ```bash
   node {baseDir}/scripts/query.mjs 北京南 上海虹桥 -d 2026-03-05 -f md
   ```

4. **For transfers**: Always verify both segments use the same station by checking `fromStation` and `toStation` in JSON output.

## 实战经验与排障（维护脚本 / Agent 查错时读）

### 余票接口是两步，不是「一次 GET 就返回列表」

1. **第一步** `GET /otn/leftTicket/query?...`：响应常为 **HTTP 302**，但 **Body 仍是 JSON**（`Content-Type: application/json`）。体内常见 `status: false`，并给出 **`c_url`**（如 `leftTicket/queryG`），含义是「真实余票请在第二步路径取」。
2. **第二步** `GET /otn/{c_url}?...`（同一套 query 参数）：服务端才返回带 **`data.result`** 的余票列表（pipe 分隔串数组）。

因此：**不能把第一步当成失败就退出**；也**不能**用「只认 HTTP 200」来判断成功——第一步可能是 302 + JSON。

### 为何 Node `fetch` 会踩坑（`Unexpected token '<'`）

- 若 **`fetch` 默认跟随重定向**：第一步 302 后客户端会去请求 `Location`（相对路径会解析到 `.../leftTicket/queryG?...`）。在某些网络/风控下，**后续**可能被导向 **HTML 错误页**（或再 302 到 `www.12306.cn/mormhweb/.../error.html`），此时再 `res.json()` 就会解析 HTML，报 **`Unexpected token '<'`**。
- **本仓库 `query.mjs` 的做法**：对余票请求使用 **`redirect: 'manual'`**，先 **读第一步响应体 JSON**，再按 **`c_url` 拼第二步 URL 请求**；若第二步正文不是 JSON（空 body、HTML），则 **明确报错**，避免把 HTML 当 JSON。

### 常见现象与处理

| 现象 | 可能原因 | 建议 |
|------|----------|------|
| `SyntaxError: Unexpected token '<'` | 跟随重定向拿到 HTML / 旧版脚本未 `manual` | 使用本仓库最新 `query.mjs`；勿对余票 URL 无脑 `res.json()` |
| 报错含 **`error.html` / `mormhweb`** | 第二步被 **风控/拦截**（空 body + 302 到错误页较常见） | 改用 **12306 官网或 App** 核对；换网络/稍后重试；**不作为脚本 bug 反复改解析逻辑** |
| 城市名查询结果「不对站」 | API 一城多站，模糊名解析到默认站 | 先用 `stations.mjs` 列出站名，再用 **精确站名** 调用 `query.mjs`（如 **无锡 → 上海虹桥**） |
| 远期日期无票/异常 | **约 15 天预售期** 等规则 | 见根目录 [`SKILL.md`](../../SKILL.md)：超出预售时对 **`当天+10 天`** 参考日查询；勿将无结果当成无车次 |

### 与机票（flightclaw）组合时的经验

- **空铁联运**算总耗时：高铁到 **虹桥** 与航班从 **浦东** 出发，需单独留 **虹桥↔浦东** 接驳（常 **1.5h+**），不要默认「到上海就赶上飞机」。
- 输出给用户时：铁路段注明 **数据来自 12306 脚本或官网**；若第二步被风控，须 **显式说明铁路段缺口** 并建议官网复核（与根目录 flightclaw 输出规范一致）。

## Technical Notes

- Data comes directly from 12306 official API (no key needed)
- Station data is cached for 7 days in `{baseDir}/data/stations.json`
- Works for all train types: G (高铁), D (动车), Z (直达), T (特快), K (快速)
- 实现细节与排障见上文 **「实战经验与排障」**；脚本内对两步接口与空响应已做防护性处理。
