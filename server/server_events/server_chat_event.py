from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json

def fire(message):
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.CHAT, message))

def fire_initial(token_object):
    manager.send_user_packet(packet_helper.build(packets.ServerPackets.CHAT, "Connected"), token_object.token)
    pass
