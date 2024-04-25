import json
from server.server_events import server_player_position_parameters_update_event

def handle(data, source_user):
    try:
        players_updated = json.loads(data)
    except json.decoder.JSONDecodeError:
        print("[BUG] failed to decode json:",data)
    #get the players whos position updated

    #TODO: Store the player positions?
    if type(players_updated) == dict and len(players_updated) == 1: # and players_updated.get(source_user): # TODO comment this out when usernames are being sent
        server_player_position_parameters_update_event.fire(data)
        #print(players_updated)
    else:
        print("[BUG] got a player position packet that is invalid:",players_updated)