from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json
import config
import importlib

def fire(indicators): #TODO only send ones that need to be updated (were changed)
    manager.broadcast_packet(packet_helper.build(packets.ServerPackets.INDICATOR_PARAMETERS_UPDATE, json.dumps(indicators)))

# send initial state of indicators
def fire_initial(token):
    model = importlib.import_module(f"simulation.models.{config.config["model"]}.model")
    manager.send_user_packet(packet_helper.build(packets.ServerPackets.INDICATOR_PARAMETERS_UPDATE, json.dumps(model.indicators)), token)