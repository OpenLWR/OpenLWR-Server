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
    "rpv_press_high_trip_a" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "mode_switch_in_shutdown_position_a" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "neutron_monitor_system_trip_a" : {
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
    "rpv_press_high_trip_b" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "mode_switch_in_shutdown_position_b" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "neutron_monitor_system_trip_b" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },

    "irm_downscale" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },

    "irm_upscale" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "irm_bdfh_upscl_trip_or_inop" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "irm_aceg_upscl_trip_or_inop" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },


    "lprm_downscale" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "aprm_downscale" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },

    "lprm_upscale" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "aprm_upscale" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "aprm_ace_upscl_trip_or_inop" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "aprm_bdf_upscl_trip_or_inop" : {
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

    "irm_a_range": {
        "positions": {
			0: -90,
			1: -75,
			2: -60,
			3: -45,
			4: -30,
			5: -15,
			6: 0,
			7: 15,
			8: 30,
			9: 45,
		},
        "position": 0,
        "lights" : {},
    },
    "irm_c_range": {
        "positions": {
			0: -90,
			1: -75,
			2: -60,
			3: -45,
			4: -30,
			5: -15,
			6: 0,
			7: 15,
			8: 30,
			9: 45,
		},
        "position": 0,
        "lights" : {},
    },
    "irm_g_range": {
        "positions": {
			0: -90,
			1: -75,
			2: -60,
			3: -45,
			4: -30,
			5: -15,
			6: 0,
			7: 15,
			8: 30,
			9: 45,
		},
        "position": 0,
        "lights" : {},
    },
    "irm_e_range": {
        "positions": {
			0: -90,
			1: -75,
			2: -60,
			3: -45,
			4: -30,
			5: -15,
			6: 0,
			7: 15,
			8: 30,
			9: 45,
		},
        "position": 0,
        "lights" : {},
    },

    "irm_b_range": {
        "positions": {
			0: -90,
			1: -75,
			2: -60,
			3: -45,
			4: -30,
			5: -15,
			6: 0,
			7: 15,
			8: 30,
			9: 45,
		},
        "position": 0,
        "lights" : {},
    },
    "irm_d_range": {
        "positions": {
			0: -90,
			1: -75,
			2: -60,
			3: -45,
			4: -30,
			5: -15,
			6: 0,
			7: 15,
			8: 30,
			9: 45,
		},
        "position": 0,
        "lights" : {},
    },
    "irm_h_range": {
        "positions": {
			0: -90,
			1: -75,
			2: -60,
			3: -45,
			4: -30,
			5: -15,
			6: 0,
			7: 15,
			8: 30,
			9: 45,
		},
        "position": 0,
        "lights" : {},
    },
    "irm_f_range": {
        "positions": {
			0: -90,
			1: -75,
			2: -60,
			3: -45,
			4: -30,
			5: -15,
			6: 0,
			7: 15,
			8: 30,
			9: 45,
		},
        "position": 0,
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
    "hpcs_p_3": {
        "positions": {
			0: 45,
			1: -45,
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
            "override" : False,
        },
    },
    "hpcs_v_1": {
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
    "hpcs_v_12": {
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
            "override" : False,
        },
    },
    "hpcs_v_23": {
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

    "rhr_p_2b": {
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
    "rhr_v_48b": {
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
    "rhr_v_3b": {
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
    "rhr_v_42b": {
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
    "rhr_v_4b": {
        "positions": {
			0: 45,
			1: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
        },
    },
    "rhr_v_6b": {
        "positions": {
			0: 45,
			1: -45,
		},
        "position": 0,
        "lights" : {
            "green" : True,
            "red" : False,
        },
    },

    "rhr_p_2c": {
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
    "rhr_p_3": {
        "positions": {
			0: 45,
			1: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
        },
    },
    "rhr_v_4c": {
        "positions": {
			0: 45,
			1: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
        },
    },
    "rhr_v_42c": {
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
    "rhr_v_24c": {
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

    #safety/relief valves

    "ms_rv_4a": {
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
    "ms_rv_4c": {
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

    "rhr_b_flow" : 0,
    "rhr_b_press" : 0,

    "rhr_c_flow" : 0,
    "rhr_c_press" : 0,

    "rpv_level_recorder_1" : 0,
    "rpv_pressure_recorder_1" : 0,

    #Neutron monitoring recorders

    "irm_a_recorder" : 0,
    "aprm_a_recorder" : 0,
    "irm_c_recorder" : 0,
    "aprm_c_recorder" : 0,

    "irm_e_recorder" : 0,
    "aprm_e_recorder" : 0,
    "irm_g_recorder" : 0,
    "rbm_a_recorder" : 0,

    "irm_b_recorder" : 0,
    "aprm_b_recorder" : 0,
    "irm_d_recorder" : 0,
    "aprm_d_recorder" : 0,

    "irm_f_recorder" : 0,
    "aprm_f_recorder" : 0,
    "irm_h_recorder" : 0,
    "rbm_b_recorder" : 0,
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

    "hpcs_init": False,

    "APRM_A_DOWNSCALE": False,
    "APRM_B_DOWNSCALE": False,
    "APRM_C_DOWNSCALE": False,
    "APRM_D_DOWNSCALE": False,
    "APRM_E_DOWNSCALE": False,
    "APRM_F_DOWNSCALE": False,

    "SELECT_SRM_A": False,
    "SRM_A_POS_IN": False,
    "SRM_A_POS_OUT": False,
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

    "SELECT_SRM_A": {
        "state" : False,
        "armed" : False,
    },
    "DET_DRIVE_IN": {
        "state" : False,
        "armed" : False,
    },
    "DET_DRIVE_OUT": {
        "state" : False,
        "armed" : False,
    },





}

pumps = {
    "hpcs_p_1" : {
        "motor_breaker_closed" : False,
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
    "hpcs_p_3" : {
        "motor_breaker_closed" : True,
        "motor_control_switch" : "hpcs_p_3",
        "bus" : "4A",
        "horsepower" : 100,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 100,
        "flow_from_rpm" : 0,
        "rated_flow" : 50,
        "header" : "hpcs_discharge_header",
        "suct_header" : "hpcs_suction_header",
    },

    "rhr_p_2b" : {
        "motor_breaker_closed" : False,
        "motor_control_switch" : "rhr_p_2b",
        "bus" : "8",
        "horsepower" : 1000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 250,
        "flow_from_rpm" : 0,
        "rated_flow" : 10000,
        "header" : "rhr_b_discharge_header",
        "suct_header" : "rhr_b_suction_header",
    },
    "rhr_p_2c" : {
        "motor_breaker_closed" : False,
        "motor_control_switch" : "rhr_p_2c",
        "bus" : "8",
        "horsepower" : 1000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 250,
        "flow_from_rpm" : 0,
        "rated_flow" : 10000,
        "header" : "rhr_c_discharge_header",
        "suct_header" : "rhr_c_suction_header",
    },
    "rhr_p_3" : {
        "motor_breaker_closed" : True,
        "motor_control_switch" : "rhr_p_3",
        "bus" : "8",
        "horsepower" : 100,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 100,
        "flow_from_rpm" : 0,
        "rated_flow" : 50,
        "header" : "rhr_p_3_discharge_header",
        "suct_header" : "rhr_c_suction_header",
    },
}

rods = {}

reactor_water_temperature = 100

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
    from simulation.models.control_room_columbia.systems import safety_relief
    safety_relief.run()
    from simulation.models.control_room_columbia.systems import irm_srm_positioner
    irm_srm_positioner.run()
    runs += 1