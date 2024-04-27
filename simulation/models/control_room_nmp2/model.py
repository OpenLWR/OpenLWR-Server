from simulation.constants.annunciator_states import AnnunciatorStates
from simulation.models.control_room_nmp2 import annunciators
from simulation.models.control_room_nmp2 import reactor_protection_system
from simulation.models.control_room_nmp2 import rod_position_information_system
from simulation.models.control_room_nmp2 import rod_drive_control_system
import math

alarms = {
    "rps_a_auto_trip" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rps_b_auto_trip" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rod_drive_accumulator_trouble" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "control_rod_out_block" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "control_rod_drift" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
}

switches = {
    "reactor_mode_switch": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
            3: -90,
		},
        "position": 2,
    },
}

values = {}

indicators = {
    "SCRAM_SOLENOID_A": True,
    "SCRAM_SOLENOID_B": True,
    "SCRAM_SOLENOID_C": True,
    "SCRAM_SOLENOID_D": True,
    "SCRAM_SOLENOID_E": True,
    "SCRAM_SOLENOID_F": True,
    "SCRAM_SOLENOID_G": True,
    "SCRAM_SOLENOID_H": True,

    #RMCS Indicators
    "RMCS_WITHDRAW_BLOCK": False,
}

buttons = {
    "SCRAM_A1": False,
    "SCRAM_B1": False,
    "SCRAM_A2": False,
    "SCRAM_B2": False,
    "ALARM_SILENCE_1": False,
    "ALARM_ACK_1": False,
    "ALARM_RESET_1": False,

    #RMCS pushbuttons
    "ACCUM_TROUBLE_RESET": False,
    "ROD_DRIFT_RESET": False,

}

rods = {}

from simulation.models.control_room_nmp2 import rod_generation
rod_generation.run(rods)

def model_run():
    #TODO: import reactor protection system and annunciator logic, and run them here
    annunciators.run(alarms,buttons)
    reactor_protection_system.run(alarms,buttons,indicators,rods,switches)
    rod_drive_control_system.run(rods,buttons)
    rod_position_information_system.run(rods,alarms)