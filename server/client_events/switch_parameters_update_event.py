import json

def handle(data):
    from simulation.global_variables.switches import switches
    switches_updated = json.loads(data)
    for switch in switches_updated:
        switches[switch]["position"] = switches_updated[switch]
    print(switches_updated)