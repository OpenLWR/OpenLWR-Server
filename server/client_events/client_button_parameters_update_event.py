import json
from server.server_events import server_button_parameters_update_event
import config
import importlib
import log

def handle(data):
    model = importlib.import_module(f"simulation.models.{config.config["model"]}.model")
    try:
        buttons_updated = json.loads(data)
    except json.decoder.JSONDecodeError:
        log.error(f"Failed to decode json: {data}")
    
    log.debug(buttons_updated)
    if type(buttons_updated) == dict and len(buttons_updated) >= 1:
        for button in buttons_updated:
            if button in model.buttons:
                model.buttons[button] = buttons_updated[button]
            else:
                log.warning(f"Got a button that is invalid from client: {button}")
    
        server_button_parameters_update_event.fire(data)
    
    else:
        log.warning(f"Got a button state packet that is invalid: {buttons_updated}")
