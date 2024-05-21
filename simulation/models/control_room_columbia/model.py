from simulation.constants.annunciator_states import AnnunciatorStates
from simulation.models.control_room_columbia import annunciators
from simulation.models.control_room_columbia import reactor_protection_system
from simulation.models.control_room_columbia import rod_position_information_system
from simulation.models.control_room_columbia import rod_drive_control_system
from simulation.models.control_room_columbia.reactor_physics import reactor_physics
from simulation.models.control_room_columbia import neutron_monitoring
from simulation.models.control_room_columbia.general_physics import ac_power
import math

from enum import IntEnum

class ReactorMode(IntEnum):
    SHUTDOWN = 0
    REFUEL = 1
    STARTUP = 2
    RUN = 3

alarms = {
    "reactor_scram_a1_and_b1_loss" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "1/2_scram_system_a" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rpv_level_low_trip_a" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rod_accumulator_trouble" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rod_out_block" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rod_drift" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },

    "reactor_scram_a2_and_b2_loss" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "1/2_scram_system_b" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rpv_level_low_trip_b" : {
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
        "position": 3,
        "lights" : {},
    },
    "hpcs_p_1": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
        },
    },
    "hpcs_v_4": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
        },
    },
    "hpcs_v_15": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
        },
    },
    "TempFW": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
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

    "hpcs_flow" : 0,
    "hpcs_press" : 0,
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

    "cr_light_normal": True,
    "cr_light_emergency": False,

    #APRM Status

    "APRM_A_UPSCALE_TRIP_OR_INOP": False,
    "APRM_B_UPSCALE_TRIP_OR_INOP": False,
    "APRM_C_UPSCALE_TRIP_OR_INOP": False,
    "APRM_D_UPSCALE_TRIP_OR_INOP": False,
    "APRM_E_UPSCALE_TRIP_OR_INOP": False,
    "APRM_F_UPSCALE_TRIP_OR_INOP": False,

    "APRM_A_UPSCALE": False,
    "APRM_B_UPSCALE": False,
    "APRM_C_UPSCALE": False,
    "APRM_D_UPSCALE": False,
    "APRM_E_UPSCALE": False,
    "APRM_F_UPSCALE": False,

    "APRM_A_DOWNSCALE": False,
    "APRM_B_DOWNSCALE": False,
    "APRM_C_DOWNSCALE": False,
    "APRM_D_DOWNSCALE": False,
    "APRM_E_DOWNSCALE": False,
    "APRM_F_DOWNSCALE": False,
}

buttons = {
    "SCRAM_A1": {
        "state" : False,
        "armed" : False,
    },
    "SCRAM_A2": {
        "state" : False,
        "armed" : False,
    },
    "SCRAM_B1": {
        "state" : False,
        "armed" : False,
    },
    "SCRAM_B2": {
        "state" : False,
        "armed" : False,
    },

    "SCRAM_RESET_A": {
        "state" : False,
        "armed" : False,
    },
    "SCRAM_RESET_B": {
        "state" : False,
        "armed" : False,
    },
    #Annunciators
    "ALARM_ACK_1": {
        "state" : False,
        "armed" : False,
    },
    "ALARM_RESET_1": {
        "state" : False,
        "armed" : False,
    },
    #2
    "ALARM_SILENCE_2": {
        "state" : False,
        "armed" : False,
    },
    "ALARM_ACK_2": {
        "state" : False,
        "armed" : False,
    },
    "ALARM_RESET_2": {
        "state" : False,
        "armed" : False,
    },

    #RMCS pushbuttons
    "ACCUM_TROUBLE_RESET": {
        "state" : False,
        "armed" : False,
    },
    "ROD_DRIFT_RESET": {
        "state" : False,
        "armed" : False,
    },

    "RMCS_INSERT_PB": {
        "state" : False,
        "armed" : False,
    },
    "RMCS_WITHDRAW_PB": {
        "state" : False,
        "armed" : False,
    },

    "hpcs_init": {
        "state" : False,
        "armed" : False,
    },


}

pumps = {
    "hpcs_p_1" : {
        "motor_breaker_closed" : True,
        "motor_control_switch" : "hpcs_p_1",
        "bus" : "4",
        "horsepower" : 3000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 1400,
        "flow_from_rpm" : 0,
        "rated_flow" : 6250,
        "header" : "hpcs_discharge_header",
        "suct_header" : "hpcs_suction_header",
    },
}

rods = {}

reactor_water_temperature = 60

from simulation.models.control_room_columbia import rod_generation
rod_generation.run(rods,buttons)

from simulation.models.control_room_columbia.general_physics import pump
pump.initialize_pumps()

from simulation.models.control_room_columbia.general_physics import fluid
fluid.initialize_headers()

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
    from simulation.models.control_room_columbia.general_physics import fluid
    fluid.run()
    from simulation.models.control_room_columbia.general_physics import pump
    pump.run()
    runs += 1