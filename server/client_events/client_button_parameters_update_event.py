import json
from server.server_events import server_button_parameters_update_event

def handle(data):
    from simulation.global_variables.buttons import buttons
    buttons_updated = json.loads(data)

    for button in buttons_updated:
        buttons[button]["state"] = buttons_updated[button]
    
    server_button_parameters_update_event.fire(data)
    
    print(buttons_updated)