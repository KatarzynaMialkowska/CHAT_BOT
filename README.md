# Rasa Discord Bot – Tournament Assistant

This project is a Rasa-powered assistant integrated with Discord. It helps users interact with fictional gaming competitions by:

- Listing open competitions
- Viewing teams and players
- Adding players to teams in specific matches
- Viewing full competition data (debugging/development use)

## Features

- Custom Rasa actions using a local JSON file (`competitions.json`)
- Discord integration with message forwarding to Rasa
- Supports intents like:
  - `list_open_competitions`
  - `request_team_players`
  - `request_all_teams`
  - `add_player_to_team`
  - `show_all`

## License

This project is for educational or internal use. Some dependencies are licensed under Apache 2.0 or other open-source licenses (see `LICENSE.txt`).
