"""China provider transformation. Existing production logic, unchanged."""


def transform_china(doc):
    management_directors = []
    if not isinstance(doc, dict):
        return management_directors
    directors_raw = doc.get("directorSupervisors", []) or []
    for entry in directors_raw:
        if not isinstance(entry, dict):
            continue
        base = entry.get("directorSupervisorBase", {}) or {}
        name = str(base.get("fullName", "") or "").strip()
        position = str(base.get("position", "") or "").strip()
        if name or position:
            management_directors.append({
                "name": name,
                "position": position,
            })
    return management_directors
