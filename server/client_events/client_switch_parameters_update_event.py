import json
from server.server_events import server_switch_parameters_update_event
import config
import importlib
import log

def handle(data):
    model = importlib.import_module(f"simulation.models.{config.config["model"]}.model")

    try:
        switches_updated = json.loads(data)
    except json.decoder.JSONDecodeError:
        log.error(f"Failed to decode json: {data}")

    if type(switches_updated) == dict and len(switches_updated) >= 1:
        for switch in switches_updated:
            if switch in model.switches and "position" in model.switches[switch]:
                model.switches[switch]["position"] = switches_updated[switch]["position"]
                #should we check if this is correct also?
                model.switches[switch]["flag"] = switches_updated[switch]["flag"]
            else:
                log.warning(f"Got a switch that is invalid from client: {switch}")
    
        server_switch_parameters_update_event.fire(switches_updated)
    else:
        log.warning(f"Got a switch position packet that is invalid: {switches_updated}")
