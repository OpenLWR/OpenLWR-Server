from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets

def fire(data,player):
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.VOIP, "%s|%s" % (data,player)))
