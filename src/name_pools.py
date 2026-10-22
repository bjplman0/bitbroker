NAME_POOLS = {
    "Personal": {
        "first_name": [
            "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", 
            "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
            "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", 
            "Lisa", "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle"
        ],
        "last_name": [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
            "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", 
            "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", 
            "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
        ]
    },
    "Small Business": {
        "adjective": [
            "Golden", "Swift", "Apex", "Reliable", "Prime", "Core", "Blue", 
            "Summit", "First", "United", "Clear", "Elite", "Dynamic", 
            "Solid", "Active", "Next", "Silver", "Iron", "Bright", "Grand"
        ],
        "noun": [
            "Valley", "Ridge", "Point", "Wave", "Star", "Path", "Stone", 
            "Line", "Horizon", "Crest", "Peak", "Shield", "Oak", "River", 
            "Light", "Way", "Mark", "Link", "Bridge", "Harbor"
        ],
        "business_type": [
            "LLC", "Services", "Consulting", "Logistics", "Solutions", 
            "Partners", "Group", "Associates", "Agency", "Studio", 
            "Ventures", "Builders", "Supply", "Management", "Trades"
        ]
    },
    "Large Corporation": {
        "corp_name": [
            "Omnis", "Veridian", "Zenith", "Nexus", "Lumina", "Aegis", "Vanguard", 
            "Globex", "Vesper", "Cobalt", "Obsidian", "Zephyr", "Titan", "Altis", 
            "Praxis", "Axiom", "Helios", "Meridian", "Strata", "Novus", "Vertex", 
            "Continuum", "Paragon", "Soliant", "Echelon", "Kymera", "Aeterna", 
            "Synergis", "Kinetix", "Acentia", "Ventoris", "Pangea", "Cryon", 
            "Thalassa", "Aether", "Volta", "Stratos", "Corvus", "Ares", "Triton"
        ],
        "corp_suffix": [
            "Holding", "Group", "Industries", "Global", "Corporation", 
            "Enterprises", "Financial", "Technologies", "Dynamics", "Manufacturing"
        ]
    },
    "Government": {
        "gov_prefix": [
            "Department of", "Bureau of", "Office of", "Ministry of", 
            "Agency for", "Commission on", "Division of", "Directorate of", 
            "Federal Bureau of", "National Office of", "Administration for"
        ],
        "gov_topic": [
            "Internal Revenue", "Vital Statistics", "Urban Planning", "Public Records",
            "Internal Affairs", "National Security", "Energy", "Transportation", 
            "Commerce", "Labor", "Health Services", "Public Safety", 
            "Environmental Protection", "Civic Infrastructure", "Telecommunications", 
            "Foreign Trade", "Cyber Defense", "Information", "Housing", 
            "Agriculture", "Science and Technology", "Emergency Management", 
            "Border Control", "Tax Administration", "Justice", "Intelligence"
        ]
    },
    "Military": {
        "mil_designation": [
            "Armored", "Signal", "Recon", "Intelligence", "Comms Relay", 
            "Tactical", "Strategic", "Logistics", "Cyber Defense", 
            "Air Defense", "Special Operations", "Expeditionary", "Assault", 
            "Electronic Warfare", "Surveillance", "Rapid Response"
        ],
        "mil_unit_type": [
            "Division", "Battalion", "Squadron", "Regiment", 
            "Brigade", "Task Force", "Wing", "Command", "Flotilla"
        ]
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
        "{number}. {mil_designation} {mil_unit_type}"
    ]
}