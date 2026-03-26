"""
携程（Ctrip）国内机票列表：通过 Playwright 打开航班列表页并解析 DOM。

免责声明：仅供个人学习与技术验证。使用前请自行阅读并遵守 https://www.ctrip.com 用户协议、
robots.txt 及适用法律；展示价格以官网为准，本工具不保证实时性与准确性。
页面结构变更会导致解析失败，需维护选择器。
"""

from __future__ import annotations

import json
import os
import re
from datetime import date
from typing import Any

from flightclaw.core.models import FlightOffer, SearchQuery, SearchResult
from flightclaw.providers.base import BaseProvider

LIST_URL = (
    "https://flights.ctrip.com/online/list/oneway-{orig}-{dest}"
    "?depdate={depdate}&cabin=y_s&sorttype=a&lowpricesource=searchform&lowpricechannel=online"
)
ROW_SELECTOR = ".flight-item.domestic"
_FNUM_RE = re.compile(r"\b([A-Z]{2}\d{3,4})\b")

# 携程「无结果」页文案（有结果时不会出现这些整段提示）
_NO_RESULT_MARKERS = (
    "未找到符合条件的航班",
    "暂时无法查询到对应价格",
)


def _page_has_no_flight_message(page: Any) -> bool:
    text: str = page.evaluate("() => (document.body && document.body.innerText) || ''")
    return any(m in text for m in _NO_RESULT_MARKERS)


def _wait_for_list_or_empty(page: Any, timeout_ms: int = 90_000) -> None:
    """等待：要么出现航班卡片，要么出现无结果提示（避免无航班时死等 selector）。"""
    page.wait_for_function(
        """() => {
          if (document.querySelector('.flight-item.domestic')) return true;
          const t = (document.body && document.body.innerText) || '';
          const markers = ['未找到符合条件的航班', '暂时无法查询到对应价格'];
          return markers.some(m => t.includes(m));
        }""",
        timeout=timeout_ms,
    )


def _scroll_to_load_lazy_rows(page: Any, *, selector: str, max_rounds: int | None = None) -> None:
    """携程列表懒加载：需多次滚到底部才会挂载更多直飞/中转卡片。"""
    rounds = max_rounds
    if rounds is None:
        try:
            rounds = int(os.environ.get("FLIGHTCLAW_CTRIP_SCROLL_ROUNDS", "35"))
        except ValueError:
            rounds = 35
    rounds = max(5, min(rounds, 60))

    last_count = -1
    stable = 0
    for _ in range(rounds):
        page.keyboard.press("End")
        page.wait_for_timeout(650)
        try:
            cur = page.locator(selector).count()
        except Exception:
            cur = 0
        if cur == last_count:
            stable += 1
            if stable >= 3:
                break
        else:
            stable = 0
        last_count = cur


def _flight_no_from_text_or_html(text: str, html: str) -> tuple[str, str]:
    """Return (flight_no, source) where source is 'text', 'html', or ''."""
    m = _FNUM_RE.search(text)
    if m:
        return m.group(1), "text"
    if html:
        m = _FNUM_RE.search(html)
        if m:
            return m.group(1), "html"
    return "", ""


def parse_flight_item_text(text: str, html: str = "") -> FlightOffer:
    """Parse one list row: visible text plus optional outerHTML for hidden flight numbers.

    东航等航司有时把航班号放在非可见节点里，innerText 不含二字码，但 outerHTML 中仍有 MUxxxx。
    """
    text_norm = " ".join(text.split())
    price_m = re.search(r"¥\s*(\d+)\s*起", text_norm)
    price = float(price_m.group(1)) if price_m else 0.0
    flight_no, fn_src = _flight_no_from_text_or_html(text_norm, html)
    times = re.findall(r"\b\d{2}:\d{2}\b", text_norm)
    dep_time = times[0] if len(times) >= 1 else ""
    arr_time = times[1] if len(times) >= 2 else ""
    note = text_norm[:500] if len(text_norm) > 500 else text_norm
    raw: dict[str, Any] = {"source": "ctrip_domestic_list", "snippet": text_norm}
    if fn_src == "html":
        raw["flight_no_from"] = "html"  # 可见文本无航班号，从 DOM 字符串补全
    return FlightOffer(
        flight_no=flight_no,
        dep_time=dep_time,
        arr_time=arr_time,
        price=price,
        currency="CNY",
        note=note,
        raw=raw,
    )


def _browser_context_kwargs() -> dict[str, Any]:
    """Optional Playwright storage state from env (login / anti-bot session)."""
    path = os.environ.get("FLIGHTCLAW_CTRIP_STORAGE_STATE", "").strip()
    if path and os.path.isfile(path):
        return {"storage_state": path}
    return {}


def _same_site_playwright(chrome: str) -> str | None:
    """Map Chrome extension sameSite to Playwright ('Lax'|'Strict'|'None' or omit)."""
    s = (chrome or "").strip().lower()
    if s in ("", "unspecified"):
        return None
    if s == "no_restriction":
        return "None"
    if s == "lax":
        return "Lax"
    if s == "strict":
        return "Strict"
    return "Lax"


def _is_chrome_extension_cookie_export(items: list[Any]) -> bool:
    if not items or not isinstance(items[0], dict):
        return False
    first = items[0]
    return "storeId" in first and "name" in first and "domain" in first


def _chrome_extension_to_playwright_cookies(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert EditThisCookie / similar Chrome export JSON to Playwright add_cookies format."""
    out: list[dict[str, Any]] = []
    for c in items:
        name = c.get("name")
        value = c.get("value")
        domain = c.get("domain")
        path = c.get("path") or "/"
        if not name or value is None or not domain:
            continue
        pc: dict[str, Any] = {
            "name": str(name),
            "value": str(value),
            "domain": str(domain),
            "path": str(path),
        }
        if not c.get("session"):
            exp = c.get("expirationDate")
            if exp is not None:
                try:
                    pc["expires"] = float(exp)
                except (TypeError, ValueError):
                    pass
        if "httpOnly" in c:
            pc["httpOnly"] = bool(c["httpOnly"])
        if "secure" in c:
            pc["secure"] = bool(c["secure"])
        ss = _same_site_playwright(str(c.get("sameSite", "")))
        if ss is not None:
            pc["sameSite"] = ss
        out.append(pc)
    return out


def _load_cookies_file(path: str) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise ValueError("Cookie JSON must be a non-empty list")
    if _is_chrome_extension_cookie_export(data):
        return _chrome_extension_to_playwright_cookies(data)
    if isinstance(data[0], dict) and "name" in data[0] and "value" in data[0] and "domain" in data[0]:
        return data
    raise ValueError("Unrecognized cookie JSON format (need Chrome export or Playwright cookie list)")


class CtripProvider(BaseProvider):
    """Headless Chromium 打开携程列表页，抓取航班卡片文本并结构化。"""

    name = "ctrip"

    def search(self, origin: str, destination: str, flight_date: date) -> SearchResult:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            raise ImportError(
                "Ctrip provider requires Playwright. Install: pip install 'flightclaw[ctrip]' "
                "&& playwright install chromium"
            ) from e

        orig = origin.strip().lower()
        dest = destination.strip().lower()
        dep = flight_date.strftime("%Y-%m-%d")
        url = LIST_URL.format(orig=orig, dest=dest, depdate=dep)

        offers: list[FlightOffer] = []
        warnings: list[str] = [
            "数据来自携程网页 DOM 解析，仅供参考，以官网为准；页面改版可能导致失败。",
            "已自动滚动列表以加载懒加载的直飞/中转方案；仍可能与官网「展开全部」不一致。",
        ]
        ctrip_says_no_flights = False
        used_session_hint = False

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx_kwargs = _browser_context_kwargs()
            if ctx_kwargs:
                used_session_hint = True
            context = browser.new_context(**ctx_kwargs)
            try:
                cookies_path = os.environ.get("FLIGHTCLAW_CTRIP_COOKIES_FILE", "").strip()
                if cookies_path and os.path.isfile(cookies_path) and not ctx_kwargs:
                    # 与 storage_state 二选一即可；若已用 storage_state 则不再叠加文件 cookies
                    context.add_cookies(_load_cookies_file(cookies_path))
                    used_session_hint = True
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=90_000)
                _wait_for_list_or_empty(page, timeout_ms=90_000)
                page.wait_for_timeout(1_500)
                _scroll_to_load_lazy_rows(page, selector=ROW_SELECTOR)
                page.wait_for_timeout(1_000)
                rows = page.eval_on_selector_all(
                    ROW_SELECTOR,
                    "elements => elements.map(e => ({ text: e.innerText, html: e.outerHTML }))",
                )
                for row in rows:
                    t = row.get("text") if isinstance(row, dict) else None
                    h = row.get("html") if isinstance(row, dict) else None
                    if not t or not str(t).strip():
                        continue
                    t_str = str(t).strip()
                    # 跳过城市标题等无价格的空卡片
                    if "¥" not in t_str and "订票" not in t_str and len(t_str) < 40:
                        continue
                    offers.append(parse_flight_item_text(t_str, html=str(h or "")))
                if not offers:
                    ctrip_says_no_flights = _page_has_no_flight_message(page)
            finally:
                context.close()
                browser.close()

        if used_session_hint:
            warnings.append(
                "已使用环境变量注入的会话（FLIGHTCLAW_CTRIP_STORAGE_STATE 或 "
                "FLIGHTCLAW_CTRIP_COOKIES_FILE）；勿将 Cookie/状态文件提交到 Git。"
            )

        q = SearchQuery(origin=origin.upper(), destination=destination.upper(), date=flight_date)
        if not offers:
            if ctrip_says_no_flights:
                warnings.append(
                    "携程页面提示：该日期/航线无航班或暂无可售价格（未找到符合条件的航班）。可换日期或航线再查。"
                )
            else:
                warnings.append("未解析到任何航班行，可能遭遇风控、选择器失效或页面结构变更。")

        return SearchResult(provider=self.name, query=q, offers=offers, warnings=warnings)
