import time
from server.server_events import server_meter_parameters_update_event
from simulation.global_variables.values import values
from simulation.global_variables.switches import switches
from simulation.global_variables.alarms import alarms
import importlib
import config


class Simulation:
    def __init__(self):
        model.init_sim_variables()
        self.timer()
            
    def timer(self):
        # TODO: proper timer
        while True:
            model.model_run()
            server_meter_parameters_update_event.fire(values)
            time.sleep(0.1)

# import the model specified in the config
model = importlib.import_module(f"simulation.models.{config.model}.model")

simulation = Simulation()
