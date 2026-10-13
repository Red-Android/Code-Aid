"""Tiny example module with an intentional discount calculation bug."""


def apply_discount(price: float, percent: float) -> float:
    """Return the price after applying a percentage discount."""
    # Intentional bug for the CodeAid demo: returns the discount amount.
    return price * percent / 100
