import time
from server.server_events import server_meter_parameters_update_event
from server.server_events import server_indicator_parameters_update_event
from server.server_events import server_alarm_parameters_update_event
import importlib
import config


class Simulation:
    def __init__(self):
        self.timer()
            
    def timer(self):
        # TODO: proper timer
        while True:
            model.model_run()
            server_meter_parameters_update_event.fire(values)
            server_indicator_parameters_update_event.fire(indicators)
            server_alarm_parameters_update_event.fire(alarms)
            time.sleep(0.1)

# import the model specified in the config
model = importlib.import_module(f"simulation.models.{config.model}.model")
from simulation.global_variables.values import values
from simulation.global_variables.switches import switches
from simulation.global_variables.alarms import alarms
from simulation.global_variables.indicators import indicators
from simulation.global_variables.buttons import buttons

simulation = Simulation()
