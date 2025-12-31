from datetime import datetime
from datetime import timedelta
issue_words = {
    "fire": 22,
    "explosion": 25,
    "electric shock": 28,
    "short circuit": 24,
    "accident": 18,
    "injured": 20,
    "open manhole": 17,
    "manhole": 14,
    "drain": 12,
    "sewer": 12,
    "sewage": 12,
    "nala": 12,
    "overflowing drain": 14,
    "sewage overflow": 14,
    "water contamination": 24,
    "contaminated": 24,
    "dirty water": 20,
    "smelly water": 18,
    "no water": 14,
    "low water pressure": 12,
    "water leakage": 11,
    "pipe burst": 16,
    "leak": 9,
    "power failure": 10,
    "power cut": 10,
    "no power": 10,
    "voltage fluctuation": 9,
    "streetlight": 6,
    "street light": 6,
    "dark street": 7,
    "not working": 5,
    "pothole": 10,
    "potholes": 10,
    "broken road": 10,
    "garbage": 10,
    "overflowing garbage": 12,
    "stagnant water": 12
}

place_words = {
    "school": 25,
    "government school": 25,
    "govt school": 25,
    "college": 22,
    "hospital": 25,
    "clinic": 22,
    "anganwadi": 22,
    "bus stop": 20,
    "railway station": 20,
    "metro station": 20,
    "market": 15,
    "bazaar": 15,
    "crowded": 15,
    "residential": 10,
    "residential area": 10,
    "housing society": 10,
    "apartment": 10,
    "slum": 12
}

impact_words = {
    "entire area": 10,
    "whole area": 10,
    "all houses": 9,
    "many houses": 8,
    "entire colony": 9,
    "full colony": 9,
    "colony": 8,
    "sector": 8,
    "locality": 8,
    "full street": 7,
    "street": 6,
    "road": 6,
    "lane": 6,
    "gali": 6,
    "my house": 3,
    "one house": 3
}


def get_issue_score(text: str) -> int:
    text = text.lower()
    score = sum(points for word, points in issue_words.items() if word in text)
    return min(score, 30)


def get_place_score(address: str) -> int:
    text = address.lower()
    for word, points in place_words.items():
        if word in text:
            return points
    return 5


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
    return 5


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

    total = issue_score + place_score + repeat_score + age_score + impact_score

    return {
        "urgency_score": total,
        "components": {
            "issue_score": issue_score,
            "place_score": place_score,
            "repeat_score": repeat_score,
            "age_score": age_score,
            "impact_score": impact_score,
        },
    }


def get_urgency_tag(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 40:
        return "medium"
    return "low"



result = get_urgency_data(
    complaint_text="contaminated dirty water supply open manhole near anganwadi.",
    address="near anganwadi kendra, ward 12, residential colony",
    similar_complaints=4,
    created_at=datetime.now() - timedelta(hours=5),
    )

print(result)
print("urgency:", get_urgency_tag(result["urgency_score"]))
