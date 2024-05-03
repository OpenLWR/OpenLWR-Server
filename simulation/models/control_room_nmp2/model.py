from simulation.constants.annunciator_states import AnnunciatorStates
from simulation.models.control_room_nmp2 import annunciators
from simulation.models.control_room_nmp2 import reactor_protection_system
from simulation.models.control_room_nmp2 import rod_position_information_system
from simulation.models.control_room_nmp2 import rod_drive_control_system
from simulation.models.control_room_nmp2.reactor_physics import reactor_physics
from simulation.models.control_room_nmp2.general_physics import ac_power
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

    "bus_014_undervoltage" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "bus_015_undervoltage" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },

    "bus_101_undervoltage" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "bus_103_undervoltage" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
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
    "cb_14-2": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
    },
    "cb_15-3": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
    },

    "cb_14-1": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
    },
    "cb_101-14": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
    },

    "cb_15-8": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
    },
    "cb_103-8": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
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

    "cb_15-3_green": True,
    "cb_15-3_red": False,

    "cb_14-2_green": True,
    "cb_14-2_red": False,

    "cb_14-1_green": True,
    "cb_14-1_red": False,

    "cb_101-14_green": True,
    "cb_101-14_red": False,

    "cb_15-8_green": True,
    "cb_15-8_red": False,

    "cb_103-8_green": True,
    "cb_103-8_red": False,

    "cr_light_normal": True,
    "cr_light_emergency": False,
}

buttons = {
    "SCRAM_A1": False,
    "SCRAM_B1": False,
    "SCRAM_A2": False,
    "SCRAM_B2": False,
    #Annunciators
    "ALARM_SILENCE_1": False,
    "ALARM_ACK_1": False,
    "ALARM_RESET_1": False,
    #2
    "ALARM_SILENCE_2": False,
    "ALARM_ACK_2": False,
    "ALARM_RESET_2": False,

    #RMCS pushbuttons
    "ACCUM_TROUBLE_RESET": False,
    "ROD_DRIFT_RESET": False,

}

rods = {}

from simulation.models.control_room_nmp2 import rod_generation
rod_generation.run(rods,buttons)
runs = 0
def model_run(delta):
    global runs
    annunciators.run(alarms,buttons)
    reactor_protection_system.run(alarms,buttons,indicators,rods,switches)
    rod_drive_control_system.run(rods,buttons)
    rod_position_information_system.run(rods,alarms,buttons)
    reactor_physics.run(rods)
    ac_power.run(switches,alarms,indicators,runs)
    runs += 1