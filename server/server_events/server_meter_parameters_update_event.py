from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json
import config
import importlib
import copy
old_values = {}
def fire(values):
    to_send = {}
    global old_values
    for value in values:
        if value in old_values:
            if old_values[value] != values[value]:
                to_send[value] = values[value]

    old_values = copy.deepcopy(values)
    
    if to_send != {}:
        manager.broadcast_packet(packet_helper.build(packets.ServerPackets.METER_PARAMETERS_UPDATE, json.dumps(to_send)))

def fire_initial(token):
    manager.send_user_packet(packet_helper.build(packets.ServerPackets.METER_PARAMETERS_UPDATE, json.dumps(old_values)),token)