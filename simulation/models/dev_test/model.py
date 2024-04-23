from simulation.global_variables.values import values
from simulation.global_variables.switches import switches
from simulation.global_variables.alarms import alarms
from simulation.global_variables.indicators import indicators

alarms_default = {
    "test1": {
        "position": 0,
    }
}

switches_default = {
    "test_switch": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 0,
    },
    "test_switch2": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 0,
    },
}

values_default = {
    "test_gauge": 0.1
}

indicators_default = {
    "lamp_test": True
}

def init_sim_variables():
    alarms = alarms_default
    switches = switches_default
    values = values_default
    indicators = indicators_default

def model_run():
    values["test_gauge"] += 0.001
    indicators["lamp_test"] = switches["test_switch"]["position"] != 1
