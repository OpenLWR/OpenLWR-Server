from simulation.constants.annunciator_states import AnnunciatorStates
import math

alarms = {
    "test_alarm" : AnnunciatorStates.CLEAR,
}

switches = {
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

values = {
    "test_gauge": 0.1
}

indicators = {
    "lamp_test": True
}

buttons = {
    "test_button": False
}

test_value = 0

def model_run(delta):
    global test_value
    if alarms == {}:
        return
    if buttons["test_button"]:
        test_value += 0.1
    values["test_gauge"] = math.sin(test_value) / 2 + 0.5
    indicators["lamp_test"] = switches["test_switch"]["position"] != 1
    alarms["test_alarm"] = AnnunciatorStates.CLEAR
    if switches["test_switch"]["position"] == 0:
        alarms["test_alarm"] = AnnunciatorStates.ACTIVE
    elif switches["test_switch"]["position"] == 2:
        alarms["test_alarm"] = AnnunciatorStates.ACTIVE_CLEAR
