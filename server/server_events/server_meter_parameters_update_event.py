from server.connection_manager import manager
from server.constants import packets
from server.helpers import packet_helper
import json

def fire(values):
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.METER_PARAMETERS_UPDATE, json.dumps(values)))