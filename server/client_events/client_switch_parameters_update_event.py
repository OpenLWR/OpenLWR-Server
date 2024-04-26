import json
from server.server_events import server_switch_parameters_update_event
import config
import importlib

def handle(data):
    model = importlib.import_module(f"simulation.models.{config.model}.model")

    try:
        switches_updated = json.loads(data)
    except json.decoder.JSONDecodeError:
        print("[BUG] failed to decode json:",data)

    if type(switches_updated) == dict and len(switches_updated) >= 1:
        for switch in switches_updated:
            if model.switches.get(switch) is not None and model.switches.get(switch).get("position") is not None:
                model.switches[switch]["position"] = switches_updated[switch]
            else:
                print("[BUG] got a switch that is invalid from client:",switch,switches_updated)
    
        server_switch_parameters_update_event.fire(data)
    else:
        print("[BUG] got a switch position packet that is invalid:",switches_updated)
