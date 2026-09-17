from src.singapore import transform_singapore

SAMPLE = {
    "officer": [
        {
            "principalName": "ALEX TAN",
            "id": "SAMPLE-ID-7781",
            "nationalityCitizenship": "COUNTRY-X",
            "position": "DIRECTOR",
            "dateOfAppointment": "2025-09-09",
            "address": {
                "type": "LOCAL",
                "streetName": "SAMPLE STREET",
                "postalCode": "100001",
                "houseNumber": "42",
            },
        }
    ]
}


def test_complete_officer_maps_unambiguous_fields_only():
    result = transform_singapore(SAMPLE)
    assert result == {
        "active_management": [
            {
                "name": "ALEX TAN",
                "role_title": "DIRECTOR",
                "alternate_name": None,
                "identifier_type": None,
                "official_identifier": "SAMPLE-ID-7781",
                "current_appointment_date": "2025-09-09",
                "nationality": "COUNTRY-X",
            }
        ]
    }


def test_missing_and_null_optional_fields_do_not_fail_or_invent_values():
    payload = {
        "officer": [
            {
                "principalName": "PARTIAL OFFICER",
                "id": None,
                "position": None,
            }
        ]
    }
    result = transform_singapore(payload)
    row = result["active_management"][0]
    assert row["name"] == "PARTIAL OFFICER"
    assert row["official_identifier"] == ""
    assert row["role_title"] == ""
    assert row["nationality"] == ""
    assert row["current_appointment_date"] == ""
    assert row["alternate_name"] is None
    assert row["identifier_type"] is None
    assert "address" not in row


def test_empty_or_null_officer_collection_returns_empty_list():
    assert transform_singapore({"officer": None}) == {"active_management": []}
    assert transform_singapore({"officer": []}) == {"active_management": []}
    assert transform_singapore({}) == {"active_management": []}
    assert transform_singapore(None) == {"active_management": []}
