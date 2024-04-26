import json
from server.server_events import server_button_parameters_update_event
import config
import importlib

def handle(data):
    model = importlib.import_module(f"simulation.models.{config.model}.model")
    try:
        buttons_updated = json.loads(data)
    except json.decoder.JSONDecodeError:
        print("[BUG] failed to decode json:",data)

    for button in buttons_updated:
        model.buttons[button] = buttons_updated[button]
    
    server_button_parameters_update_event.fire(data)
    
    print(buttons_updated)
    if type(buttons_updated) == dict and len(buttons_updated) >= 1:
        for button in buttons_updated:
            if button in model.buttons:
                model.buttons[button] = buttons_updated[button]
            else:
                print("[BUG] got a button that is invalid from client:",button,buttons_updated)
    
        server_button_parameters_update_event.fire(data)
    
        #print(buttons_updated)
    else:
        print("[BUG] got a button state packet that is invalid:",buttons_updated)
