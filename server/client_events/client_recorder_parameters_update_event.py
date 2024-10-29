import json
import config
import importlib
import log

def handle(data):
    model = importlib.import_module(f"simulation.models.{config.config["model"]}.model")
    try:
        data = data.split("|")
        chart_name = data[0]
        buttons_updated = json.loads(data[1])
    except json.decoder.JSONDecodeError:
        log.error(f"Failed to decode json: {data}")
    
    if type(buttons_updated) == dict and len(buttons_updated) >= 1:
        for button in buttons_updated:
            model.recorders[chart_name].button_updated(button,buttons_updated[button])
    else:
        log.warning(f"Got a recorder state packet that is invalid.")
