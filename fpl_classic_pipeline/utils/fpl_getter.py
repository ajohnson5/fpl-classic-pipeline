import requests


def manager_id_from_league_api(league_id):
    """Returns list of manager_ids from a classic league"""

    url = (
        f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
    )
    req = requests.get(url).json()
    manager_ids = []
    for manager in req["standings"]["results"]:
        manager_ids.append(
            {"manager_id": manager["entry"], "name": manager["entry_name"]}
        )

    return manager_ids


def gw_stats_api(gw):
    """Returns a list of dictionaries of all players stats for the gameweek (gw)"""

    url = f"https://fantasy.premierleague.com/api/event/{gw}/live/"
    req = requests.get(url).json()
    player_list = []
    for player in req["elements"]:
        player_list.append({"id": player["id"], "gameweek": int(gw), **player["stats"]})
    return player_list


def player_api():
    """Returns a list of dictionaries for all Premier League player this season"""

    player_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    player_req = requests.get(player_url).json()
    player_list = []
    for element in player_req["elements"]:
        dict_ = {
            "id": element["id"],
            "first_name": element["first_name"],
            "second_name": element["second_name"],
            "full_name": element["first_name"] + " " + element["second_name"],
            "team_id": element["team"],
            "position": element["element_type"],
        }
        player_list.append(dict_)
    return player_list


def team_api():
    """Returns a list dictionaries of every team in the Premier League this season"""

    team_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    team_req = requests.get(team_url).json()
    team_list = []
    for team in team_req["teams"]:
        team_list.append({"team_id": team["id"], "team_name": team["name"]})
    return team_list


def manager_gw_picks_api(gw, manager_id):
    """Returns a list of dictionaries of all picks a manager made in a gameweek"""
    url = f"https://fantasy.premierleague.com/api/entry/{manager_id}/event/{gw}/picks/"
    req = requests.get(url).json()
    manager_picks = []
    try:
        for player in req["picks"]:
            manager_picks.append(
                {
                    "manager_id": int(manager_id),
                    "id": player["element"],
                    "multiplier": player["multiplier"],
                }
            )
        return manager_picks
    except KeyError:
        return None
    except TypeError:
        return None


def gw_completed_api(gw):
    """Returns true is all games have been completed for gw and false otherwise"""
    url = f"https://fantasy.premierleague.com/api/fixtures/?event={gw}"
    req = requests.get(url).json()
    for fixture in req:
        if not fixture["finished"]:
            return False
    return True


def manager_gw_performance_api(gw, manager_id):
    """Returns a list of dictionaries of a managers performance in a given gameweek."""
    try:
        url = (
            f"https://fantasy.premierleague.com/api/"
            f"entry/{manager_id}/event/{gw}/picks/"
        )
        req = requests.get(url).json()
        manager_gw_stats = [
            {
                "manager_id": int(manager_id),
                "chip": req["active_chip"],
                **req["entry_history"],
            }
        ]
        return manager_gw_stats
    except KeyError:
        return None
    except TypeError:
        return None
