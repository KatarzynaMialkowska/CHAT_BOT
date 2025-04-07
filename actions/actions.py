from typing import Dict, Text, Any, List
from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import Tracker
import json
import os

class ActionListOpenCompetitions(Action):
    def name(self) -> Text:
        return "action_list_open_competitions"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        competitions_path = os.path.join(os.path.dirname(__file__), '..', 'data_json', 'competitions.json')
        try:
            with open(competitions_path) as file:
                competitions_data = json.load(file)
        except FileNotFoundError:
            dispatcher.utter_message(text="Error: Failed to found json file.")
            return []
        except json.JSONDecodeError:
            dispatcher.utter_message(text="Error: Failed to decode json file.")
            return []

        message = ""
        for comp in competitions_data["competitions"]:
            if comp["status"] == "open":
                message += f"\n{comp['name']} on {comp['date']}:\n"
                for match in comp["matches"]:
                    teams = " vs ".join([team["name"] for team in match["teams"]])
                    message += f"  Match: {teams} at {match['start_time']} - {match['end_time']}\n"

        if message:
            dispatcher.utter_message(text=f"Open competitions with upcoming matches:\n{message}")
        else:
            dispatcher.utter_message(text="There are no open competitions with upcoming matches at the moment.")

        return []

class ActionListTeamsAndPlayers(Action):
    def name(self) -> Text:
        return "action_list_teams_and_players"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        team_name = next(tracker.get_latest_entity_values("team"), None)
        competition_name = next(tracker.get_latest_entity_values("competition"), None)

        competitions_path = os.path.join(os.path.dirname(__file__), '..', 'data_json', 'competitions.json')
        try:
            with open(competitions_path) as file:
                competitions_data = json.load(file)
        except FileNotFoundError:
            dispatcher.utter_message(text="Error: Failed to found json file.")
            return []
        except json.JSONDecodeError:
            dispatcher.utter_message(text="Error: Failed to decode json file.")
            return []

        message = "Details not found."
        found = False
        for comp in competitions_data["competitions"]:
            if comp["name"] == competition_name:
                for match in comp["matches"]:
                    for team in match["teams"]:
                        if team["name"] == team_name:
                            players_details = "\n".join([f"Player ID: {player['id']}, Name: {player['name']}" for player in team["players"]])
                            message = f"Players in {team_name} from match {match['id']}:\n{players_details}"
                            found = True
                            break
                    if found:
                        break
                if found:
                    break

        dispatcher.utter_message(text=message)
        return []


class ActionListAllTeams(Action):
    def name(self) -> Text:
        return "action_list_all_teams"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        competition_name = next(tracker.get_latest_entity_values("competition"), None)
        competitions_path = os.path.join(os.path.dirname(__file__), '..', 'data_json', 'competitions.json')
        try:
            with open(competitions_path) as file:
                competitions_data = json.load(file)
        except FileNotFoundError:
            dispatcher.utter_message(text="Error: Failed to found json file.")
            return []
        except json.JSONDecodeError:
            dispatcher.utter_message(text="Error: Failed to decode json file.")
            return []

        message = "Competition not found."
        for competition in competitions_data["competitions"]:
            if competition["name"] == competition_name:
                message = f"Teams in {competition_name}:\n"
                for match in competition["matches"]:
                    message += f"Match {match['id']} from {match['start_time']} to {match['end_time']}:\n"
                    for team in match["teams"]:
                        player_details = "\n".join([f"  - Player ID: {player['id']} {player['name']}" for player in team["players"]])
                        message += f"  {team['name']} with players:\n{player_details}\n"
                break

        dispatcher.utter_message(text=message)
        return []

class ActionAddPlayerToTeam(Action):
    def name(self):
        return "action_add_player_to_team"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        player_name = tracker.get_slot('player_name')
        team_name = tracker.get_slot('team')
        competition_name = tracker.get_slot('competition')
        match_id = tracker.get_slot('match')
        dispatcher.utter_message(text=f"match {match_id}")
        competitions_path = os.path.join(os.path.dirname(__file__), '..', 'data_json', 'competitions.json')
        try:
            with open(competitions_path) as file:
                competitions_data = json.load(file)
        except FileNotFoundError:
            dispatcher.utter_message(text="Error: Failed to found json file.")
            return []
        except json.JSONDecodeError:
            dispatcher.utter_message(text="Error: Failed to decode json file.")
            return []

        player_added = False
        matches_updated = []
        competition_info = ""
        for comp in competitions_data['competitions']:
            if comp['name'] == competition_name and comp['status'] == "open":
                competition_info = f"{comp['name']} on {comp['date']}"
                for match in comp['matches']:
                    if match_id == "all":
                        for team in match['teams']:
                            if team['name'] == team_name and len(team['players']) < team['max_players']:
                                new_player_id = max((player['id'] for player in team['players']), default=0) + 1
                                team['players'].append({"id": new_player_id, "name": player_name})
                                matches_updated.append(f"{match['id']} from {match['start_time']} to {match['end_time']}")
                                player_added = True

                    elif match['id'] == match_id:
                        for team in match['teams']:
                            if team['name'] == team_name and len(team['players']) < team['max_players']:
                                new_player_id = max((player['id'] for player in team['players']), default=0) + 1
                                team['players'].append({"id": new_player_id, "name": player_name})
                                matches_updated.append(f"{match['id']} from {match['start_time']} to {match['end_time']}")
                                player_added = True
                                break
                    if player_added and match_id != "all":
                        break
                if player_added and match_id != "all":
                    break

        if player_added:
            with open(competitions_path, 'w') as file:
                json.dump(competitions_data, file, indent=4)
            match_list = ', '.join(matches_updated)
            dispatcher.utter_message(text=f"Player {player_name} (ID: {new_player_id}) added to team {team_name} \nin matches: {match_list}\nfor competition: {competition_info}.")
        else:
            dispatcher.utter_message(text="Failed to add player due to full team or invalid match.")

        return []

class ActionShowAllJson(Action):
    def name(self) -> Text:
        return "action_show_all_json"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        competitions_path = os.path.join(os.path.dirname(__file__), '..', 'data_json', 'competitions.json')
        try:
            with open(competitions_path, 'r') as file:
                competitions_data = json.load(file)
                dispatcher.utter_message(text=json.dumps(competitions_data, indent=4))
        except FileNotFoundError:
            dispatcher.utter_message(text="Error: Failed to found json file.")
        except json.JSONDecodeError:
            dispatcher.utter_message(text="Error: Failed to decode json file.")
        return []