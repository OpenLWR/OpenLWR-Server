from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets

def fire(switches):
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.SWITCH_PARAMETERS_UPDATE, switches))