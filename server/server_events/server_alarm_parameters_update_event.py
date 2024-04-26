from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json

from enum import IntEnum

class AnnunciatorStates(IntEnum):
    CLEAR = 0
    ACTIVE = 1
    ACKNOWLEDGED = 2
    ACTIVE_CLEAR = 3

def fire(alarms): #TODO only send ones that need to be updated (were changed)
    data = {}
    silent = {
        "1" : {"F":True,"S":True}, # F - Fast S - Slow
    }

    for alarm in alarms:
        data[alarm] = alarms[alarm]["state"]
        if not data[alarm]["silent"] and alarms[alarm]["state"] == AnnunciatorStates.ACTIVE:
            silent[alarms[alarm]["group"]]["F"] = False
        
        if not data[alarm]["silent"] and alarms[alarm]["state"] == AnnunciatorStates.ACTIVE_CLEAR:
            silent[alarms[alarm]["group"]]["S"] = False
    
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.ALARM_PARAMETERS_UPDATE, f"{json.dumps(data)}|{json.dumps(silent)}"))

# send initial state of indicators
def fire_initial(token):
    from simulation.global_variables.alarms import alarms
    manager.send_user_packet(packet_helper.build(packets.ServerPackets.ALARM_PARAMETERS_UPDATE, json.dumps(alarms)), token)