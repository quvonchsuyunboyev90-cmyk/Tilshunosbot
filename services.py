import requests
from config import RAPIDAPI_KEY, RAPIDAPI_HOST


def call_sport_api(endpoint_path, params=None):
    url = "https://" + RAPIDAPI_HOST + endpoint_path

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params or {},
            timeout=20,
        )

        print(f"[SPORT API] {endpoint_path} -> {response.status_code}")

        return response

    except Exception as e:
        print(f"[SPORT API ERROR] {e}")
        return None


def search_team(team_name):
    response = call_sport_api(
        "/football-teams-search",
        {"search": team_name},
    )

    if response is None:
        return None

    if response.status_code != 200:
        return None

    try:
        data = response.json()

        suggestions = data.get("response", {}).get(
            "suggestions",
            [],
        )

        for item in suggestions:
            if item.get("type") == "team":
                return item

        return None

    except Exception:
        return None
