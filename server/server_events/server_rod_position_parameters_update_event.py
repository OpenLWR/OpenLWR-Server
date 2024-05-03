from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json
import config
import importlib
old_rods = {}

def fire(rods): #TODO only send ones that need to be updated (were changed)
    new_rods = json.loads(json.dumps(rods)) # hack to copy this properly
    #TODO: figure out why the initial rod packet doesnt send right
    #NOTE: temporarily commented this part of the code so it will send every rod at all times
    for rod_name,rod in rods.items():
        if old_rods.get(rod_name) == rod:
            del new_rods[rod_name]
        else:
            old_rods[rod_name] = json.loads(json.dumps(rod)) # hack to copy this properly
            #print("sent:",rod_name)

    if new_rods != {}:
        manager.broadcast_packet(packet_helper.build(packets.ServerPackets.ROD_POSITION_PARAMETERS_UPDATE, json.dumps(new_rods)))

# send initial state of indicators
def fire_initial(token):
    #model = importlib.import_module(f"simulation.models.{config.model}.model")
    #manager.send_user_packet(packet_helper.build(packets.ServerPackets.ROD_POSITION_PARAMETERS_UPDATE, json.dumps(old_rods)), token)
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.ROD_POSITION_PARAMETERS_UPDATE, json.dumps(old_rods)))