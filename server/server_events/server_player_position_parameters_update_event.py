from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json

def fire():
    positions = {}
    for tk in manager.tokens:
        position = manager.tokens[tk].position
        positions[manager.tokens[tk].username] = position

    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.PLAYER_POSITION_PARAMETERS_UPDATE, json.dumps(positions)))

def fire_initial(token):
    positions = {}
    for tk in manager.tokens:
        position = manager.tokens[tk].position
        positions[manager.tokens[tk].username] = position

    manager.send_user_packet(packet_helper.build(packets.ServerPackets.PLAYER_POSITION_PARAMETERS_UPDATE, json.dumps(positions)),token)
    pass