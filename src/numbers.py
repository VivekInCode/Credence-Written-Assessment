"""Safe numeric parsing. Invalid provider values must not crash a transform."""

from decimal import Decimal, InvalidOperation


def is_missing(value) -> bool:
    """True when a field is absent for calculation purposes. Numeric zero is present."""
    return value is None or value == ""


def to_decimal(value):
    """Return Decimal for a usable number, otherwise None."""
    if is_missing(value) or isinstance(value, bool):
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not number.is_finite():
        return None
    return number
