import json
from server.server_events import server_switch_parameters_update_event

def handle(data):
    from simulation.global_variables.switches import switches
    switches_updated = json.loads(data)

    for switch in switches_updated:
        switches[switch]["position"] = switches_updated[switch]
    
    server_switch_parameters_update_event.fire(data)
    
    print(switches_updated)