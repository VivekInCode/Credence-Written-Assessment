"""Shared formatting helpers used by provider transformers."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def format_with_commas(value) -> str:
    """Existing helper: format numeric share counts with thousands separators."""
    if value is None or value == "":
        return ""
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return str(value)
    if number == number.to_integral_value():
        return f"{int(number):,}"
    return str(value)


def format_percentage(value, *, max_decimal_places=None) -> str:
    """
    Deterministic percentage string.

    Whole numbers are rendered without a decimal (25 -> "25").
    Non-integers keep significant digits without float noise (12.5 -> "12.5").
    Calculated values may pass max_decimal_places=4; supplied values omit it
    so the provider figure is not rewritten.
    """
    if value is None or value == "":
        return ""
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return ""
    if not number.is_finite():
        return ""
    if max_decimal_places is not None:
        quantum = Decimal("1").scaleb(-max_decimal_places)
        number = number.quantize(quantum, rounding=ROUND_HALF_UP)
    if number == number.to_integral_value():
        return str(int(number))
    text = format(number, "f").rstrip("0").rstrip(".")
    return text
