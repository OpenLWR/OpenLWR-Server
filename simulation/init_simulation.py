import time
import math
import importlib
from server.server_events import server_meter_parameters_update_event
from server.server_events import server_indicator_parameters_update_event
from server.server_events import server_alarm_parameters_update_event
import config

# import the model specified in the config
model = importlib.import_module(f"simulation.models.{config.model}.model")

class Simulation:
    def __init__(self):
        self.timestep = 0.1 # time between model steps
        self.default_timestep = 0.1 # what is 1x speed
        self.minimum_speedup_drop = 2 # skip sending packets if we exceed this many times 1x speed
        self.timesteps = 0 # how many timesteps did we take
        self.prev_delta = 0
        self.timer()

    def timer(self):
        while True:
            start = time.perf_counter()
            model.model_run(self.prev_delta)
            drop = 0
            if (self.default_timestep/self.timestep) >= self.minimum_speedup_drop:
                drop = self.timesteps % math.floor((self.default_timestep/self.timestep)/self.minimum_speedup_drop)
            if drop == 0: # prevent flooding clients on high speedups
                server_meter_parameters_update_event.fire(model.values)
                server_indicator_parameters_update_event.fire(model.indicators)
                server_alarm_parameters_update_event.fire(model.alarms)
            end = time.perf_counter()
            delta = end - start
            if self.timestep - delta < 0:
                print(f"[ALERT] simulation cant keep up, time we have:{self.timestep}, time we took: {delta}")
            else:
                time.sleep(self.timestep - delta)
            self.timesteps += 1
            self.prev_delta = delta

simulation = Simulation()
