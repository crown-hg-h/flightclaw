"""Chrome extension cookie export → Playwright format."""

from flightclaw.providers.ctrip import (
    _chrome_extension_to_playwright_cookies,
    _is_chrome_extension_cookie_export,
)


def test_detect_chrome_export():
    raw = [{"storeId": "0", "name": "a", "value": "b", "domain": ".x.com", "path": "/"}]
    assert _is_chrome_extension_cookie_export(raw) is True


def test_chrome_to_playwright_minimal():
    raw = [
        {
            "domain": ".ctrip.com",
            "expirationDate": 1808991219,
            "hostOnly": False,
            "httpOnly": False,
            "name": "UBT_VID",
            "path": "/",
            "sameSite": "unspecified",
            "secure": False,
            "session": False,
            "storeId": "0",
            "value": "x",
        }
    ]
    out = _chrome_extension_to_playwright_cookies(raw)
    assert len(out) == 1
    assert out[0]["name"] == "UBT_VID"
    assert out[0]["value"] == "x"
    assert out[0]["domain"] == ".ctrip.com"
    assert out[0]["expires"] == 1808991219.0
    assert "sameSite" not in out[0] or out[0].get("sameSite") is None
