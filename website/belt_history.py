import json
import os
from datetime import date
from typing import List, Dict, Optional
import requests

BELT_HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'belt_history.json')


def load_history() -> List[Dict[str, str]]:
    if os.path.exists(BELT_HISTORY_FILE):
        with open(BELT_HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []


def save_history(history: List[Dict[str, str]]) -> None:
    with open(BELT_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def get_current_champion() -> Optional[str]:
    """Return the team currently holding the belt."""
    history = load_history()
    return history[-1]['Winner'] if history else None


def add_new_champion(
    champion: str,
    game_date: str,
    loser: str,
    score: str = "",
    notes: Optional[str] = None,
) -> None:
    """Append a new belt result to the history file."""
    history = load_history()
    history.append(
        {
            "Date": game_date,
            "Winner": champion,
            "Loser": loser,
            "Score": score,
            "Notes": notes,
        }
    )
    history = load_history()
    return history[-1]['champion'] if history else None


def add_new_champion(champion: str, game_date: str) -> None:
    history = load_history()
    history.append({'date': game_date, 'champion': champion})
    save_history(history)


def update_belt() -> Optional[str]:
    """Check an external sports API to update the belt holder.

    This implementation uses the College Football Data API. The function
    fetches today's games for the current champion and updates the belt
    history if the champion loses.
    """
    champion = get_current_champion()
    if not champion:
        return None

    today = date.today()
    url = 'https://api.collegefootballdata.com/games'
    params = {
        'year': today.year,
        'team': champion,
        'startDate': today.isoformat(),
        'endDate': today.isoformat(),
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        games = response.json()
    except Exception as exc:  # pragma: no cover - network call not tested
        print(f'Could not update belt: {exc}')
        return None

    if not games:
        # Champion did not play today
        return champion

    game = games[0]
    home_team = game.get('home_team')
    away_team = game.get('away_team')
    home_score = game.get('home_points', 0)
    away_score = game.get('away_points', 0)

    if champion == home_team:
        champion_score, opponent_score = home_score, away_score
        opponent_team = away_team
    else:
        champion_score, opponent_score = away_score, home_score
        opponent_team = home_team

    if champion_score is None or opponent_score is None:
        return champion

    if champion_score < opponent_score:
        score_str = f"{opponent_score}-{champion_score}"
        add_new_champion(
            opponent_team,
            today.isoformat(),
            loser=champion,
            score=score_str,
            notes=None,
        )

        add_new_champion(opponent_team, today.isoformat())

        return opponent_team

    return champion
