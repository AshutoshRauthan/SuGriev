from datetime import datetime

# --------------------------------------------------
# High Risk Keywords (Public Safety Boost)
# --------------------------------------------------
HIGH_RISK_KEYWORDS = [
    "live wire",
    "electric shock",
    "current leak",
    "fire",
    "explosion",
    "open manhole",
    "water contamination",
    "sewage",
    "dengue",
    "malaria",
    "health"
]

# --------------------------------------------------
# Issue Severity Keywords
# --------------------------------------------------
issue_words = {
    # Electrical & Fire
    "fire": 26,
    "explosion": 28,
    "transformer blast": 28,
    "electric shock": 30,
    "live wire": 30,
    "current leak": 26,
    "short circuit": 24,
    "bijli": 18,

    # Accidents & Physical Hazards
    "accident": 20,
    "injured": 22,
    "open manhole": 22,
    "manhole": 16,
    "road cave-in": 18,

    # Drainage & Sanitation
    "drain": 12,
    "nala": 14,
    "jammed drain": 16,
    "overflowing drain": 16,
    "sewer": 14,
    "sewage": 14,
    "septic tank": 15,
    "water logging": 18,
    "stagnant water": 16,

    # Water Supply
    "water contamination": 28,
    "contaminated": 26,
    "dirty water": 22,
    "smelly water": 18,
    "no water": 15,
    "low water pressure": 12,
    "water leakage": 12,
    "pipe burst": 18,
    "hand pump": 10,
    "borewell": 10,

    # Power Supply
    "power failure": 12,
    "power cut": 12,
    "no power": 12,
    "voltage fluctuation": 10,

    # Roads
    "pothole": 12,
    "potholes": 12,
    "broken road": 12,

    # Waste & Health
    "garbage": 12,
    "overflowing garbage": 14,
    "kooda": 12,
    "dumping waste": 14,
    "dengue": 22,
    "mosquitoes":20,
    "malaria": 20,

    "health":20,
    "no doctor":15
}

# --------------------------------------------------
# Sensitive Location Keywords
# --------------------------------------------------
place_words = {
    "school": 26,
    "government school": 26,
    "govt school": 26,
    "college": 22,
    "hospital": 28,
    "clinic": 24,
    "anganwadi": 24,
    "bus stop": 22,
    "bus stand": 22,
    "railway station": 22,
    "metro station": 22,
    "market": 16,
    "bazaar": 16,
    "crowded": 16,
    "residential area": 12,
    "housing society": 12,
    "apartment": 12,
    "slum": 14
}

# --------------------------------------------------
# Impact Scope Keywords
# --------------------------------------------------
impact_words = {
    "entire area": 12,
    "whole area": 12,
    "all houses": 10,
    "many houses": 9,
    "entire colony": 10,
    "full colony": 10,
    "colony": 9,
    "sector": 9,
    "locality": 9,
    "full street": 8,
    "street": 7,
    "road": 7,
    "lane": 6,
    "gali": 6,
    "my house": 3,
    "one house": 3
}

# --------------------------------------------------
# Scoring Functions
# --------------------------------------------------
def get_issue_score(text: str) -> int:
    text = text.lower()
    score = sum(points for word, points in issue_words.items() if word in text)
    return min(score, 30)


def get_place_score(address: str) -> int:
    text = address.lower()
    for word, points in place_words.items():
        if word in text:
            return points
    return 6


def get_repeat_count_score(count: int) -> int:
    if count >= 6:
        return 20
    if count >= 4:
        return 15
    if count >= 2:
        return 10
    if count == 1:
        return 6
    return 0


def get_age_hours_score(created_at: datetime) -> int:
    hours_old = (datetime.now() - created_at).total_seconds() / 3600
    return min(int(hours_old), 15)


def get_impact_score(text: str, address: str) -> int:
    combined = f"{text} {address}".lower()
    for word, points in impact_words.items():
        if word in combined:
            return points
    return 6


def get_risk_multiplier(text: str) -> float:
    text = text.lower()
    for word in HIGH_RISK_KEYWORDS:
        if word in text:
            return 1.25
    return 1.0


# --------------------------------------------------
# Main Urgency Calculator
# --------------------------------------------------
def get_urgency_data(
    complaint_text: str,
    address: str,
    similar_complaints: int,
    created_at: datetime
) -> dict:
    issue_score = get_issue_score(complaint_text)
    place_score = get_place_score(address)
    repeat_score = get_repeat_count_score(similar_complaints)
    age_score = get_age_hours_score(created_at)
    impact_score = get_impact_score(complaint_text, address)

    base_score = (
        issue_score
        + place_score
        + repeat_score
        + age_score
        + impact_score
    )

    multiplier = get_risk_multiplier(complaint_text)
    total_score = min(100,(int(base_score * multiplier)*1.5))

    return {
        "urgency_score": total_score,
        "components": {
            "issue_score": issue_score,
            "place_score": place_score,
            "repeat_score": repeat_score,
            "age_score": age_score,
            "impact_score": impact_score,
            "risk_multiplier": multiplier
        }
    }


def get_urgency_tag(score: int) -> str:
    if score >= 85:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 40:
        return "medium"
    return "low"