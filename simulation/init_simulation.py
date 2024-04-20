import time
from server.server_events import meter_parameters_update_event
from simulation.global_variables.values import values
from simulation.global_variables.switches import switches
from simulation.global_variables.alarms import alarms

class Simulation:
    def __init__(self):
        self.values = values
        self.switches = switches
        self.alarms = alarms

        self.timer()
            
    def timer(self):
        # TODO: proper timer
        while True:
            self.values["test_gauge"] += 0.001
            time.sleep(0.1)
            meter_parameters_update_event.fire(self.values)

simulation = Simulation()
