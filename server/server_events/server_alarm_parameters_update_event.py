from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json

def fire(alarms): #TODO only send ones that need to be updated (were changed)
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.ALARM_PARAMETERS_UPDATE, json.dumps(alarms)))

# send initial state of indicators
def fire_initial(token):
    from simulation.global_variables.alarms import alarms
    manager.send_user_packet(packet_helper.build(packets.ServerPackets.ALARM_PARAMETERS_UPDATE, json.dumps(alarms)), token)