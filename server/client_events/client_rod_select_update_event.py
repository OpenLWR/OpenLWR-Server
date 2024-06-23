import json
import config
import importlib

def handle(data):
    model = importlib.import_module(f"simulation.models.{config.model}.model")
    try:
        rod_selected = json.loads(data)
    except json.decoder.JSONDecodeError:
        print("[BUG] failed to decode json:",data)
    
    if type(rod_selected) == str and len(rod_selected) >= 1:
        if rod_selected in model.rods:
            from simulation.models.control_room_columbia import rod_drive_control_system
            if not rod_drive_control_system.select_block:
                for rod in model.rods:
                    model.rods[rod]["select"] = False

                model.rods[rod_selected]["select"] = True

           

        else:
            print("[BUG] got a rod select that is invalid from client:",rod_selected)

    else:
        print("[BUG] got a rod select packet that is invalid:",rod_selected)
