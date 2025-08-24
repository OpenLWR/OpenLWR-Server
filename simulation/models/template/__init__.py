from . import model
model_obj = model.Model()

step_config = {
    "main": {
        "default_timestep": 0.1, # what is 1x speed
        "function": model_obj.step, # the function you want to be called
    },
    "slow": {
        "default_timestep": 1, # what is 1x speed
        "function": model_obj.step_slow, # the function you want to be called
    },
}