import time
import importlib
import config
from threading import Thread
class Simulation:
    def __init__(self):
        # get the user configured values
        self.step_config = model.step_config

        # add the extra variables we need
        for name in self.step_config:
            step_loop = self.step_config[name]
            step_loop["timestep"] = step_loop["default_timestep"]
            step_loop["timesteps"] = 0
            step_loop["prev_delta"] = step_loop["timestep"]
            step_loop["simulation_normal"] = Thread(target=self.timer, args=(name, step_loop,))
            step_loop["simulation_normal"].start()
            
    def timer(self, name, step_loop):
        while True:
            start = time.perf_counter()
            step_loop["function"](step_loop["prev_delta"])
            end = time.perf_counter()
            delta = end - start

            if step_loop["timestep"] - delta < 0:
                log.warning(f"[ALERT] {name} cant keep up, time target was {step_loop["timestep"]}, but actual time was {delta}")
            else:
                time.sleep(step_loop["timestep"] - delta)

            step_loop["timesteps"] += 1
            step_loop["prev_delta"] = max(step_loop["timestep"], delta)

# import the model specified in the config
model = importlib.import_module(f"simulation.models.{config.config["model"]}")

simulation = Simulation()
