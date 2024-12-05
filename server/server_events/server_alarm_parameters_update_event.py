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
        "2" : {"F":True,"S":True},
        "3" : {"F":True,"S":True},
        "4" : {"F":True,"S":True},
        "5" : {"F":True,"S":True},
        "6" : {"F":True,"S":True},
    }

    for alarm in alarms:
        data[alarm] = {"state" : alarms[alarm]["state"],"silenced" : alarms[alarm]["silenced"]}
        alarm = alarms[alarm]
        if alarm["group"] == "-1":
            continue
        if not alarm["silenced"] and (alarm["state"] == AnnunciatorStates.ACTIVE):
            silent[alarm["group"]]["F"] = False
        
        if not alarm["silenced"] and (alarm["state"] == AnnunciatorStates.ACTIVE_CLEAR):
            silent[alarm["group"]]["S"] = False
    
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.ALARM_PARAMETERS_UPDATE, f"{json.dumps(data)}|{json.dumps(silent)}"))

# send initial state of indicators
def fire_initial(token):
    silent = {
        "1" : {"F":True,"S":True}, # F - Fast S - Slow
        "2" : {"F":True,"S":True},
    }
    #manager.send_user_packet(packet_helper.build(packets.ServerPackets.ALARM_PARAMETERS_UPDATE, f"{json.dumps(alarms)}|{json.dumps(silent)}"),token)