# Football API Module

from services import *

print("Football API yuklandi")
def get_team_details(team_id):
    """
    Jamoa haqida batafsil ma'lumot qaytaradi.
    """
    return call_sport_api(
        "/football-team-detail",
        {"teamId": team_id}
    )
