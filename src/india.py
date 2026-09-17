"""India provider transformation. Existing production behaviour plus missing-percentage calc."""

from src.formatting import format_percentage, format_with_commas
from src.numbers import is_missing, to_decimal


def _shareholding_percentage(record: dict, total_issued_shares) -> str:
    supplied = record.get("percentage_holding", None)
    if not is_missing(supplied):
        # Preserve a valid supplied value (including 0). Do not recalculate.
        if to_decimal(supplied) is None:
            return ""
        return format_percentage(supplied)

    shares = to_decimal(record.get("no_of_shares"))
    total = to_decimal(total_issued_shares)
    if shares is None or total is None or total == 0:
        return ""
    return format_percentage((shares / total) * 100, max_decimal_places=4)


def transform_india(section_data):
    """
    Transform India director_shareholdings.

    Existing rules preserved:
    - "Not available" -> empty list
    - exclude records with date_of_cessation set
    - dedupe on din_pan, then full_name
    """
    if not section_data or not isinstance(section_data, list):
        return []
    company = section_data[0] if isinstance(section_data[0], dict) else {}
    raw = company.get("director_shareholdings", [])
    if raw == "Not available":
        director_shareholdings = []
    else:
        director_shareholdings = [
            s for s in (raw or [])
            if isinstance(s, dict) and s.get("date_of_cessation") is None
        ]

    seen_share_keys = set()
    shareholdings = []
    total_issued_shares = company.get("total_issued_shares")
    for s in director_shareholdings:
        key = s.get("din_pan") or s.get("full_name")
        if not key or key in seen_share_keys:
            continue
        seen_share_keys.add(key)
        shareholdings.append({
            "Name": s.get("full_name", ""),
            "Designation": s.get("designation", ""),
            "Shareholding (%)": _shareholding_percentage(s, total_issued_shares),
            "Number of Share": format_with_commas(s.get("no_of_shares", "")),
        })
    return shareholdings
