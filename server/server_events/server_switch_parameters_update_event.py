from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json

def fire(switches):
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.SWITCH_PARAMETERS_UPDATE, switches))

# used when a client first connects to sync up switch positions
def fire_initial(token):
    from simulation.global_variables.switches import switches
    switches_to_send = {}
    for switch in switches:
        switches_to_send[switch] = switches[switch]["position"]
    manager.send_user_packet(packet_helper.build(packets.ServerPackets.SWITCH_PARAMETERS_UPDATE, json.dumps(switches_to_send)), token)