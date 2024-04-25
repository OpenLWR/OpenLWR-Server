import json
from server.server_events import server_switch_parameters_update_event

def handle(data):
    from simulation.global_variables.switches import switches
    try:
        switches_updated = json.loads(data)
    except json.decoder.JSONDecodeError:
        print("[BUG] failed to decode json:",data)
    if type(switches_updated) == dict and len(switches_updated) >= 1:
        for switch in switches_updated:
            if switch in switches:
                switches[switch]["position"] = switches_updated[switch]
            else:
                print("[BUG] got a switch that is invalid from client:",switch,switches_updated)
    
        server_switch_parameters_update_event.fire(data)
    
        print(switches_updated)
    else:
        print("[BUG] got a switch position packet that is invalid:",switches_updated)
