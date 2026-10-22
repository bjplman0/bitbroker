NAME_POOLS = {
    "Personal": {
        "first_name": [],
        "last_name": []
    },
    "Small Business": {
        "adjective": [],
        "noun": [],
        "business_type": []
    },
    "Large Corporation": {
        "corp_name": [],
        "corp_suffix": []
    },
    "Government": {
        "gov_prefix": [],
        "gov_topic": []
    },
    "Military": {
        "mil_designation": [],
        "mil_unit_type": []
    }
}

NAME_TEMPLATES = {
    "Personal": [
        "{first_name} {last_name}"
    ],
    "Small Business": [
        "{adjective} {noun} {business_type}"
    ],
    "Large Corporation": [
        "{corp_name} {corp_suffix}"
    ],
    "Government": [
        "{gov_prefix} {gov_topic}"
    ],
    "Military": [
        "{mil_designation} {mil_unit_type}"
    ]
}