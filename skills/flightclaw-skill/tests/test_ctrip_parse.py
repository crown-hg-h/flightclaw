from flightclaw.providers.ctrip import parse_flight_item_text


def test_parse_flight_item_with_fnum():
    text = (
        "中国国航 CA1589 波音777(大) 当日低价 20:30 首都国际机场T3 22:40 虹桥国际机场T2 "
        "赠接送机85折优惠券 ¥500起 经济舱2.4折 订票"
    )
    o = parse_flight_item_text(text)
    assert o.flight_no == "CA1589"
    assert o.dep_time == "20:30"
    assert o.arr_time == "22:40"
    assert o.price == 500.0
    assert o.currency == "CNY"


def test_parse_flight_item_mu_from_html_when_absent_in_text():
    """东航等：innerText 无航班号时，用 outerHTML 中的二字码补全。"""
    text = (
        "东方航空 21:00 首都国际机场T2 23:10 虹桥国际机场T2 赠接送机85折优惠券 ¥502起 经济舱2.4折 订票"
    )
    html = '<div class="flight-item" data-x="1">MU5128</div>'
    o = parse_flight_item_text(text, html=html)
    assert o.flight_no == "MU5128"
    assert o.raw.get("flight_no_from") == "html"
    assert o.price == 502.0
    assert o.dep_time == "21:00"


def test_parse_flight_item_text_only_still_empty_fnum_without_html():
    text = (
        "东方航空 21:00 首都国际机场T2 23:10 虹桥国际机场T2 赠接送机85折优惠券 ¥502起 经济舱2.4折 订票"
    )
    o = parse_flight_item_text(text)
    assert o.flight_no == ""
    assert o.price == 502.0
