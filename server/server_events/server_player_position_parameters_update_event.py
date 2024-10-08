from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json

def fire():
    positions = {}
    for tk in manager.tokens:
        position = manager.tokens[tk].position
        rotation = manager.tokens[tk].rotation
        positions[manager.tokens[tk].username] = {}
        positions[manager.tokens[tk].username]["position"] = position
        positions[manager.tokens[tk].username]["rotation"] = rotation

    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.PLAYER_POSITION_PARAMETERS_UPDATE, json.dumps(positions)))

def fire_initial(token):
    positions = {}
    for tk in manager.tokens:
        position = manager.tokens[tk].position
        rotation = manager.tokens[tk].rotation
        positions[manager.tokens[tk].username] = {}
        positions[manager.tokens[tk].username]["position"] = position
        positions[manager.tokens[tk].username]["rotation"] = rotation

    manager.send_user_packet(packet_helper.build(packets.ServerPackets.PLAYER_POSITION_PARAMETERS_UPDATE, json.dumps(positions)),token)