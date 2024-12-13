from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
from simulation.init_simulation import simulation as sim
import json

def fire(message):
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.CHAT, message))

def fire_initial(token_object):
    if token_object.websocket.remote_address[0] == "127.0.0.1":
        manager.send_user_packet(packet_helper.build(packets.ServerPackets.CHAT, "Connected (commands are available)"), token_object.token)
    else:
        manager.send_user_packet(packet_helper.build(packets.ServerPackets.CHAT, "Connected"), token_object.token)

    if not sim.running:
        manager.send_user_packet(packet_helper.build(packets.ServerPackets.CHAT, "Simulation paused."), token_object.token)
    
    pass
