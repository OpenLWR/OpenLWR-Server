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
            "page":recorders[recorder].page,
            "elements":recorders[recorder].elements,
            "display_on":recorders[recorder].display_on,
        }

    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.RECORDER, json.dumps(recorder_table)))
