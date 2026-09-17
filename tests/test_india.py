from src.india import transform_india

INDIA_SAMPLE = [
    {
        "total_issued_shares": 10000,
        "director_shareholdings": [
            {
                "din_pan": "ID-IND-101",
                "full_name": "ARUN SAMPLE",
                "designation": "Director",
                "date_of_cessation": None,
                "no_of_shares": 1200,
                "percentage_holding": 12.5,
            },
            {
                "din_pan": "ID-IND-303",
                "full_name": "NEEL TEST",
                "designation": "Director",
                "date_of_cessation": None,
                "no_of_shares": 2500,
                "percentage_holding": None,
            },
            {
                "din_pan": "ID-IND-202",
                "full_name": "RAVI DEMO",
                "designation": "Director",
                "date_of_cessation": "2025-01-10",
                "no_of_shares": 400,
                "percentage_holding": None,
            },
        ],
    }
]


def test_supplied_percentage_is_preserved():
    rows = transform_india(INDIA_SAMPLE)
    arun = next(r for r in rows if r["Name"] == "ARUN SAMPLE")
    assert arun["Shareholding (%)"] == "12.5"
    assert arun["Number of Share"] == "1,200"


def test_missing_percentage_is_calculated():
    rows = transform_india(INDIA_SAMPLE)
    neel = next(r for r in rows if r["Name"] == "NEEL TEST")
    assert neel["Shareholding (%)"] == "25"


def test_ceased_director_is_excluded():
    rows = transform_india(INDIA_SAMPLE)
    names = [r["Name"] for r in rows]
    assert "RAVI DEMO" not in names
    assert names == ["ARUN SAMPLE", "NEEL TEST"]


def test_zero_supplied_percentage_is_not_recalculated():
    payload = [
        {
            "total_issued_shares": 10000,
            "director_shareholdings": [
                {
                    "din_pan": "ID-IND-000",
                    "full_name": "ZERO HOLDING",
                    "designation": "Director",
                    "date_of_cessation": None,
                    "no_of_shares": 2500,
                    "percentage_holding": 0,
                }
            ],
        }
    ]
    rows = transform_india(payload)
    assert rows[0]["Shareholding (%)"] == "0"


def test_invalid_share_data_does_not_fail_or_invent_percentage():
    payload = [
        {
            "total_issued_shares": 0,
            "director_shareholdings": [
                {
                    "din_pan": "A",
                    "full_name": "ZERO TOTAL",
                    "designation": "Director",
                    "date_of_cessation": None,
                    "no_of_shares": 100,
                    "percentage_holding": None,
                },
                {
                    "din_pan": "B",
                    "full_name": "NULL TOTAL",
                    "designation": "Director",
                    "date_of_cessation": None,
                    "no_of_shares": 100,
                    "percentage_holding": None,
                },
            ],
        }
    ]
    rows = transform_india(payload)
    assert rows[0]["Shareholding (%)"] == ""

    payload[0]["total_issued_shares"] = None
    rows = transform_india(payload)
    assert all(r["Shareholding (%)"] == "" for r in rows)

    payload[0]["total_issued_shares"] = 10000
    payload[0]["director_shareholdings"][0]["no_of_shares"] = None
    payload[0]["director_shareholdings"][1]["no_of_shares"] = None
    rows = transform_india(payload)
    assert all(r["Shareholding (%)"] == "" for r in rows)
    assert len(rows) == 2


def test_omitted_percentage_key_is_calculated():
    payload = [
        {
            "total_issued_shares": 10000,
            "director_shareholdings": [
                {
                    "din_pan": "ID-IND-404",
                    "full_name": "KEY OMITTED",
                    "designation": "Director",
                    "date_of_cessation": None,
                    "no_of_shares": 2500,
                }
            ],
        }
    ]
    rows = transform_india(payload)
    assert rows[0]["Shareholding (%)"] == "25"


def test_invalid_row_does_not_block_later_calculated_percentage():
    payload = [
        {
            "total_issued_shares": 10000,
            "director_shareholdings": [
                {
                    "din_pan": "ID-IND-501",
                    "full_name": "BAD SHARES",
                    "designation": "Director",
                    "date_of_cessation": None,
                    "no_of_shares": None,
                    "percentage_holding": None,
                },
                {
                    "din_pan": "ID-IND-502",
                    "full_name": "GOOD SHARES",
                    "designation": "Director",
                    "date_of_cessation": None,
                    "no_of_shares": 2500,
                },
            ],
        }
    ]
    rows = transform_india(payload)
    assert rows[0]["Shareholding (%)"] == ""
    assert rows[1]["Name"] == "GOOD SHARES"
    assert rows[1]["Shareholding (%)"] == "25"


def test_repeating_calculated_percentage_is_capped_at_four_decimals():
    payload = [
        {
            "total_issued_shares": 3,
            "director_shareholdings": [
                {
                    "din_pan": "ID-IND-601",
                    "full_name": "REPEATING PCT",
                    "designation": "Director",
                    "date_of_cessation": None,
                    "no_of_shares": 1,
                }
            ],
        }
    ]
    rows = transform_india(payload)
    assert rows[0]["Shareholding (%)"] == "33.3333"
