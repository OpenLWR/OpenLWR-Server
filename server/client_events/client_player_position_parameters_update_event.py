import json
from server.server_events import server_player_position_parameters_update_event
import log

def handle(data, source_user):
    try:
        players_updated = json.loads(data)
    except json.decoder.JSONDecodeError:
        log.error(f"Failed to decode json: {data}")
    #get the players whos position updated

    #TODO: Store the player positions?
    if type(players_updated) == dict and len(players_updated) == 1:
        server_player_position_parameters_update_event.fire(data)
    else:
        log.warning(f"Got a player position packet that is invalid: {players_updated}")