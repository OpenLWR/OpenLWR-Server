from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets

def fire(data,player):

    for user in manager.tokens:
        manager.send_user_packet(packet_helper.build(packets.ServerPackets.VOIP, "%s|%s" % (data,player)),manager.tokens[user].token)
