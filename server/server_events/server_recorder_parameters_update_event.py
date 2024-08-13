from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json
import config

def fire(recorders): 

    recorder_table = {}
    for recorder in recorders:
        recorder_table[recorder] = {
            "channels":recorders[recorder].channels,
        }

    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.RECORDER, json.dumps(recorder_table)))
