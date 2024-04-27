import time
from server.server_events import server_meter_parameters_update_event
from server.server_events import server_indicator_parameters_update_event
from server.server_events import server_alarm_parameters_update_event

import importlib
import config

# import the model specified in the config
model = importlib.import_module(f"simulation.models.{config.model}.model")

class Simulation:
    def __init__(self):
        self.timer()
            
    def timer(self):
        # TODO: proper timer
        while True:
            model.model_run()
            server_meter_parameters_update_event.fire(model.values)
            server_indicator_parameters_update_event.fire(model.indicators)
            server_alarm_parameters_update_event.fire(model.alarms)
            #rod position updates is in RPIS model
            time.sleep(0.1)

simulation = Simulation()
