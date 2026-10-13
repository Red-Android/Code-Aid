from discounts import apply_discount


def test_applies_percentage_discount():
    assert apply_discount(100, 20) == 80


def test_zero_percent_keeps_original_price():
    assert apply_discount(50, 0) == 50


def test_full_discount_returns_zero():
    assert apply_discount(100, 100) == 0
