from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json

def fire(players):
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.PLAYER_POSITION_PARAMETERS_UPDATE, players))

# used when a client first connects to sync up switch positions
def fire_initial(token):
    #TODO: we have no players stored, so we cant send the player's the positions.
    pass