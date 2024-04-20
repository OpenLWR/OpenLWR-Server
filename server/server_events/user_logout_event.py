from server.connection_manager import manager
from server.constants import packets
from server.helpers import packet_helper
import json

async def fire(username):
    await manager.broadcast_packet(packet_helper.build(packets.ServerPackets.USER_LOGOUT, username))