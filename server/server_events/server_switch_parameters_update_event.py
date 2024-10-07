from server.helpers import packet_helper
from server.connection_manager import manager
from server.constants import packets
import json
import config
import importlib
import copy
old_switches = {}
def fire(switches,is_model=False):
    model = importlib.import_module(f"simulation.models.{config.config["model"]}.model")
    to_send = {}
    global old_switches
    if is_model == True:
        for switch in switches:
            if switch in old_switches:
                if old_switches[switch] != switches[switch]:
                    to_send[switch] = {"position" : switches[switch]["position"], "lights" : switches[switch]["lights"], "flag" : switches[switch]["flag"]}

        old_switches = copy.deepcopy(switches)
    else:
        for switch in switches:
            if type(switches[switch]) == int:
                to_send[switch] = {"position" : switches[switch], "lights" : model.switches[switch]["lights"], "flag" : model.switches[switch]["flag"]}
            else:
                to_send[switch] = {"position" : switches[switch]["position"], "lights" : model.switches[switch]["lights"], "flag" : switches[switch]["flag"]}

    if to_send != {}:
        manager.broadcast_packet(packet_helper.build(packets.ServerPackets.SWITCH_PARAMETERS_UPDATE, json.dumps(to_send)))

# used when a client first connects to sync up switch positions
def fire_initial(token):
    model = importlib.import_module(f"simulation.models.{config.config["model"]}.model")
    switches_to_send = {}
    for switch in model.switches:
        switches_to_send[switch] = {"position" : model.switches[switch]["position"], "lights" : model.switches[switch]["lights"], "flag" : model.switches[switch]["flag"]}
    manager.send_user_packet(packet_helper.build(packets.ServerPackets.SWITCH_PARAMETERS_UPDATE, json.dumps(switches_to_send)), token)