from simulation.constants.annunciator_states import AnnunciatorStates
from simulation.models.control_room_columbia import annunciators
from simulation.models.control_room_columbia import reactor_protection_system
from simulation.models.control_room_columbia import rod_position_information_system
from simulation.models.control_room_columbia import rod_drive_control_system
from simulation.models.control_room_columbia.reactor_physics import reactor_physics
from simulation.models.control_room_columbia import neutron_monitoring
from simulation.models.control_room_columbia.general_physics import ac_power
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

values = {
    "four_rod_br": 1,
    "four_rod_bl": 60,
    "four_rod_tr": 15,
    "four_rod_tl": -21,

    "srm_a_counts" : 20,
    "srm_b_counts" : 20,
    "srm_c_counts" : 20,
    "srm_d_counts" : 20,

    "srm_a_period" : 0,
    "srm_b_period" : 0,
    "srm_c_period" : 0,
    "srm_d_period" : 0,

    "aprm_temporary" : 0,
}

indicators = {
    "SCRAM_A1": True,
    "SCRAM_A2": True,
    "SCRAM_A3": True,
    "SCRAM_A4": True,
    "SCRAM_A5": False,
    "SCRAM_A6": False,

    "SCRAM_B1": True,
    "SCRAM_B2": True,
    "SCRAM_B3": True,
    "SCRAM_B4": True,
    "SCRAM_B5": False,
    "SCRAM_B6": False,

    #RMCS Indicators
    "RMCS_INSERT_BLOCK": False,
    "RMCS_WITHDRAW_BLOCK": False,
    #Rod Motion Controls
    "RMCS_SETTLE": False,
    "RMCS_INSERT": False,
    "RMCS_WITHDRAW": False,

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

    "RMCS_INSERT_PB": False,
    "RMCS_WITHDRAW_PB": False,


}

rods = {}

from simulation.models.control_room_columbia import rod_generation
rod_generation.run(rods,buttons)
runs = 0
def model_run(delta):
    global runs
    annunciators.run(alarms,buttons)
    reactor_protection_system.run(alarms,buttons,indicators,rods,switches)
    rod_drive_control_system.run(rods,buttons)
    rod_position_information_system.run(rods,alarms,buttons)
    reactor_physics.run(rods)
    neutron_monitoring.run(alarms,buttons,indicators,rods,switches,values)
    ac_power.run(switches,alarms,indicators,runs)
    runs += 1