from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json

def fire(indicators): #TODO only send ones that need to be updated (were changed)
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.INDICATOR_PARAMETERS_UPDATE, json.dumps(indicators)))

# send initial state of indicators
def fire_initial(token):
    from simulation.global_variables.indicators import indicators
    manager.send_user_packet(packet_helper.build(packets.ServerPackets.INDICATOR_PARAMETERS_UPDATE, json.dumps(indicators)), token)