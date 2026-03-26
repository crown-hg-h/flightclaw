# Flightclaw — 示例

总览见 [`SKILL.md`](../SKILL.md)。命令字段与 JSON 结构见 [`reference.md`](reference.md)。

## 今日日期

```bash
# 已 pip install 时（在 skills/flightclaw-skill 目录或全局 PATH 有 flightclaw）
flightclaw --json today

# 免安装：在仓库根目录执行
python skills/flightclaw-skill/scripts/flight.py --json today
```

## 占位检索（不联网）

```bash
# 与 12306 技能包对称：从仓库根用脚本（可不 pip install）
python skills/flightclaw-skill/scripts/flight.py --json search --from BJS --to SHA --date 2026-04-01 --provider example

# 若已 pip install -e skills/flightclaw-skill
flightclaw --json search --from BJS --to SHA --date 2026-04-01 --provider example
```

## 携程（需 `pip install -e ".[ctrip]"` + `playwright install chromium`）

```bash
export FLIGHTCLAW_CTRIP_COOKIES_FILE="/本机安全路径/ctrip-cookies.json"   # 可选，建议

# 免安装：在仓库根目录执行（需已安装 ctrip 依赖与 Chromium，见上文小标题）
python skills/flightclaw-skill/scripts/flight.py --json search --from BJS --to LJG --date 2026-04-03 --provider ctrip

# 若已 pip install -e ".[ctrip]" 且 PATH 有 flightclaw
flightclaw --json search --from BJS --to LJG --date 2026-04-03 --provider ctrip
```

## REPL

```bash
flightclaw
# flightclaw> today
# flightclaw> search --from BJS --to SHA --date 2026-04-01 --provider example
# flightclaw> exit
```

## 模块方式（PATH 无入口脚本时）

```bash
cd skills/flightclaw-skill && python -m flightclaw --json providers
```

## 12306 高铁/火车（Node，在仓库根目录执行）

```bash
# 上海虹桥 → 杭州东，某日 G 车，Markdown 表输出到 stdout
node skills/12306-skill/scripts/query.mjs 上海虹桥 杭州东 -d 2026-03-26 -t G -f md

# 原始 JSON
node skills/12306-skill/scripts/query.mjs 北京 上海 --json

# 车站解析
node skills/12306-skill/scripts/stations.mjs 杭州
```

**远期出行日**：若乘车日尚未进入预售（常见距出发约 15 天内才开售），用 **`当天日期 + 10 天`** 作为 `-d` 的参考日（见 [`SKILL.md`](../SKILL.md) 与 [`skills/12306-skill/SKILL.md`](../skills/12306-skill/SKILL.md)），输出时注明「参考日 ≠ 用户出行日」。
