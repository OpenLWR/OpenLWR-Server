import json
from server.server_events import server_player_position_parameters_update_event

def handle(data):
    players_updated = json.loads(data)
    #get the players whos position updated

    #TODO: Store the player positions?
    
    server_player_position_parameters_update_event.fire(data)
    
    print(players_updated)