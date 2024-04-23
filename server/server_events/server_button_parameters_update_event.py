from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json

def fire(buttons): #TODO only send ones that need to be updated (were changed)
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.BUTTON_PARAMETERS_UPDATE, buttons))

# send initial state of indicators
def fire_initial(token):
    from simulation.global_variables.buttons import buttons
    manager.send_user_packet(packet_helper.build(packets.ServerPackets.BUTTON_PARAMETERS_UPDATE, json.dumps(buttons)), token)