import requests
from config import RAPIDAPI_KEY, RAPIDAPI_HOST

BASE_URL = f"https://{RAPIDAPI_HOST}"

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
}


def api_get(endpoint, params=None):
    try:
        r = requests.get(
            BASE_URL + endpoint,
            headers=HEADERS,
            params=params or {},
            timeout=20
        )

        if r.status_code == 200:
            return r.json()

        print(f"API ERROR {r.status_code}")
        return None

    except Exception as e:
        print(e)
        return None


def live_matches():
    return api_get("/football-live-all")


def standings(league_id):
    return api_get("/football-get-standing-all", {
        "leagueid": league_id
    })


def team(team_id):
    return api_get("/football-team-detail", {
        "teamid": team_id
    })


def injuries(team_id):
    return api_get("/football-team-injuries", {
        "teamid": team_id
    })


def odds(match_id):
    return api_get("/football-match-odds", {
        "matchid": match_id
    })


def h2h(team1, team2):
    return api_get("/football-head-to-head", {
        "teamOneId": team1,
        "teamTwoId": team2
    })
