"""Singapore provider -> global active_management. Map only unambiguous fields."""


def _as_text(value) -> str:
    if value is None:
        return ""
    return str(value)


def transform_singapore(payload):
    """
    Map Singapore officer records to active_management.

    Mapped:
      principalName -> name
      position -> role_title
      id -> official_identifier (type unknown; identifier_type left unmapped)
      dateOfAppointment -> current_appointment_date
      nationalityCitizenship -> nationality

    Unmapped (no invented semantics):
      alternate_name, identifier_type, address
    """
    if not isinstance(payload, dict):
        return {"active_management": []}

    officers = payload.get("officer")
    if not officers or not isinstance(officers, list):
        return {"active_management": []}

    active_management = []
    for officer in officers:
        if not isinstance(officer, dict):
            continue
        active_management.append({
            "name": _as_text(officer.get("principalName")),
            "role_title": _as_text(officer.get("position")),
            "alternate_name": None,
            "identifier_type": None,
            "official_identifier": _as_text(officer.get("id")),
            "current_appointment_date": _as_text(officer.get("dateOfAppointment")),
            "nationality": _as_text(officer.get("nationalityCitizenship")),
        })
    return {"active_management": active_management}
