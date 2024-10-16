from simulation.constants.annunciator_states import AnnunciatorStates
from simulation.models.control_room_columbia import annunciators
from simulation.models.control_room_columbia import reactor_protection_system
from simulation.models.control_room_columbia import rod_position_information_system
from simulation.models.control_room_columbia import rod_drive_control_system
from simulation.models.control_room_columbia.reactor_physics import reactor_physics
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
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
        "box": "Box1",
		"window": "1-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "1/2_scram_system_a" : {
        "alarm" : False,
        "box": "Box1",
		"window": "3-4",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rpv_level_low_trip_a" : {
        "alarm" : False,
        "box": "Box1",
		"window": "2-3",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rpv_press_high_trip_a" : {
        "alarm" : False,
        "box": "Box1",
		"window": "2-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "mode_switch_in_shutdown_position_a" : {
        "alarm" : False,
        "box": "Box1",
		"window": "5-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "neutron_monitor_system_trip_a" : {
        "alarm" : False,
        "box": "Box1",
		"window": "3-3",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "msiv_closure_trip_a" : {
        "alarm" : False,
        "box": "Box1",
		"window": "2-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },

    "rod_accumulator_trouble" : {
        "alarm" : False,
        "box": "Box1",
		"window": "6-7",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rpis_or_dmm_inop" : {
        "alarm" : False,
        "box": "Box1",
		"window": "1-7",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rod_out_block" : {
        "alarm" : False,
        "box": "Box1",
		"window": "2-7",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rod_drift" : {
        "alarm" : False,
        "box": "Box1",
		"window": "5-7",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },

    "reactor_scram_a2_and_b2_loss" : {
        "alarm" : False,
        "box": "Box2",
		"window": "1-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "1/2_scram_system_b" : {
        "alarm" : False,
        "box": "Box2",
		"window": "3-4",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rpv_level_low_trip_b" : {
        "alarm" : False,
        "box": "Box2",
		"window": "2-3",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rpv_press_high_trip_b" : {
        "alarm" : False,
        "box": "Box2",
		"window": "2-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "mode_switch_in_shutdown_position_b" : {
        "alarm" : False,
        "box": "Box2",
		"window": "5-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "neutron_monitor_system_trip_b" : {
        "alarm" : False,
        "box": "Box2",
		"window": "3-3",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "msiv_closure_trip_b" : {
        "alarm" : False,
        "box": "Box2",
		"window": "2-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },

    "irm_downscale" : {
        "alarm" : False,
        "box": "Box1",
		"window": "4-5",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },

    "irm_upscale" : {
        "alarm" : False,
        "box": "Box1",
		"window": "3-5",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "irm_bdfh_upscl_trip_or_inop" : {
        "alarm" : False,
        "box": "Box2",
		"window": "1-5",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "irm_aceg_upscl_trip_or_inop" : {
        "alarm" : False,
        "box": "Box1",
		"window": "2-5",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },


    "rbm_downscale" : {
        "alarm" : False,
        "box": "Box2",
		"window": "6-6",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "lprm_downscale" : {
        "alarm" : False,
        "box": "Box2",
		"window": "5-6",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "aprm_downscale" : {
        "alarm" : False,
        "box": "Box2",
		"window": "4-6",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },

    "rbm_upscale_or_inop" : {
        "alarm" : False,
        "box": "Box2",
		"window": "3-5",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "lprm_upscale" : {
        "alarm" : False,
        "box": "Box2",
		"window": "2-5",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "aprm_upscale" : {
        "alarm" : False,
        "box": "Box2",
		"window": "2-6",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "aprm_ace_upscl_trip_or_inop" : {
        "alarm" : False,
        "box": "Box1",
		"window": "1-5",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "aprm_bdf_upscl_trip_or_inop" : {
        "alarm" : False,
        "box": "Box2",
		"window": "1-6",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },

    "setpoint_setdown_active" : {
        "alarm" : False,
        "box": "Box2",
		"window": "2-7",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },

    #P602.A6
    "recirc_a_or_b_high_flow_delta" : {
        "alarm" : False,
        "box": "P602_A6",
		"window": "6-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rpv_level_low_limit" : {
        "alarm" : False,
        "box": "P602_A6",
		"window": "6-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "feedwater_pump_trip_limit" : {
        "alarm" : False,
        "box": "P602_A6",
		"window": "5-8",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },

    #P601.A11
    "msiv_half_trip_system_b" : {
        "alarm" : False,
        "box": "P601_A11",
		"window": "5-3",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "rc_2_half_trip" : {
        "alarm" : False,
        "box": "P601_A11",
		"window": "2-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "nssss_isol_rpv_level_low_b" : {
        "alarm" : False,
        "box": "P601_A11",
		"window": "2-4",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "nssss_main_condsr_vac_low_bypass_b" : {
        "alarm" : False,
        "box": "P601_A11",
		"window": "6-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "nssss_isol_main_condenser_vac_low_b" : {
        "alarm" : False,
        "box": "P601_A11",
		"window": "5-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "main_steam_line_press_low" : {
        "alarm" : False,
        "box": "P601_A11",
		"window": "1-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "msiv_isol_sys_b_lvl/tmp_bypass" : {
        "alarm" : False,
        "box": "P601_A11",
		"window": "1-4",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },

    #P601.A12
    "msiv_half_trip_system_a" : {
        "alarm" : False,
        "box": "P601_A12",
		"window": "2-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "rc_1_half_trip" : {
        "alarm" : False,
        "box": "P601_A12",
		"window": "4-3",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "nssss_isol_rpv_level_low_a" : {
        "alarm" : False,
        "box": "P601_A12",
		"window": "2-4",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "nssss_main_condsr_vac_low_bypass_a" : {
        "alarm" : False,
        "box": "P601_A12",
		"window": "2-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "nssss_isol_main_condenser_vac_low_a" : {
        "alarm" : False,
        "box": "P601_A12",
		"window": "3-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "msiv_isol_sys_a_lvl/tmp_bypass" : {
        "alarm" : False,
        "box": "P601_A12",
		"window": "1-4",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },

    #RHR A/LPCS
    "lpcs_rhr_a_actuated" : {
        "alarm" : False,
        "box": "P601_A3",
		"window": "1-3",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "lpcs_rhr_a_init_rpv_level_low" : {
        "alarm" : False,
        "box": "P601_A3",
		"window": "6-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },

    #RHR B/C
    "rhr_bc_actuated" : {
        "alarm" : False,
        "box": "P601_A2",
		"window": "1-4",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "rhr_bc_init_rpv_level_low" : {
        "alarm" : False,
        "box": "P601_A2",
		"window": "1-5",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },

    #P601.A4 (RCIC)
    "rcic_actuated" : {
        "alarm" : False,
        "box": "P601_A4",
		"window": "1-2",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },
    "rcic_turbine_trip" : {
        "alarm" : False,
        "box": "P601_A4",
		"window": "1-5",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "2",
        "silenced" : False,
    },

    #HPCS
    "hpcs_actuated" : {
        "alarm" : False,
        "box": "P601_A1",
		"window": "1-6",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "3",
        "silenced" : False,
    },

    #P840.A1
    "turbine_a_tripped" : {
        "alarm" : False,
        "box": "P840_A1",
		"window": "1-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "5",
        "silenced" : False,
    },
    "turbine_a_overspeed_trip" : {
        "alarm" : False,
        "box": "P840_A1",
		"window": "6-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "5",
        "silenced" : False,
    },
    "turbine_b_tripped" : {
        "alarm" : False,
        "box": "P840_A1",
		"window": "1-5",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "5",
        "silenced" : False,
    },
    "turbine_b_overspeed_trip" : {
        "alarm" : False,
        "box": "P840_A1",
		"window": "6-5",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "5",
        "silenced" : False,
    },


    #FCP-1

    "tg_bldg_471_elect_swgr_bay" : {
        "alarm" : False,
        "box": "FCP1_A",
		"window": "1-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "4",
        "silenced" : False,
    },
    "tg_bldg_471_elect_swgr_bay_trouble" : {
        "alarm" : False,
        "box": "FCP1_A",
		"window": "2-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "4",
        "silenced" : False,
    },
    "tg_bldg_471_elect_swgr_bay_fire" : {
        "alarm" : False,
        "box": "FCP1_A",
		"window": "3-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "4",
        "silenced" : False,
    },

    #FCP-2

    "sys_7_wet_pipe_tg_bldg_471_elect_swgr_bay" : {
        "alarm" : False,
        "box": "FCP2_A",
		"window": "1-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "4",
        "silenced" : False,
    },
    "sys_7_wet_pipe_tg_bldg_471_elect_swgr_bay_trouble" : {
        "alarm" : False,
        "box": "FCP2_A",
		"window": "2-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "4",
        "silenced" : False,
    },
    "sys_7_wet_pipe_tg_bldg_471_elect_swgr_bay_fire" : {
        "alarm" : False,
        "box": "FCP2_A",
		"window": "3-1",
        "state" : AnnunciatorStates.CLEAR,
        "group" : "4",
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
        "position": 0,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
    },

    #safety/relief valves

        "ms_rv_5b": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_3d": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_5c": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_4d": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_4b": {
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
        "flag" : "green",
        "momentary" : False,
    },
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
        "flag" : "green",
        "momentary" : False,
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_1a": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_2b": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_1c": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_1b": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_2c": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_1d": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_3c": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_2d": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_2a": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_3b": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_rv_3a": {
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
        "flag" : "green",
        "momentary" : False,
    },

    "rcic_v_45": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "rcic_v_1": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "rcic_v_8": {
        "positions": {
			0: 45,
			1: -45,
		},
        "position": 0,
        "lights" : {
            "green" : True,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "rcic_v_63": {
        "positions": {
			0: 45,
			1: -45,
		},
        "position": 0,
        "lights" : {
            "green" : True,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "rcic_v_68": {
        "positions": {
			0: 45,
			1: -45,
		},
        "position": 0,
        "lights" : {
            "green" : True,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },

    #flow paths
    "rcic_v_13": {
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
        "flag" : "green",
        "momentary" : False,
    },

    "rcic_v_31": {
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
        "flag" : "green",
        "momentary" : False,
    },

    #LPCS

    "lpcs_p_1": {
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
        "flag" : "green",
        "momentary" : False,
    },

    "lpcs_v_5": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "lpcs_v_11": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "lpcs_v_12": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "lpcs_v_1": {
        "positions": {
			0: 45,
			1: -45,
		},
        "position": 0,
        "lights" : {
            "green" : True,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },

    #RHR A
    "rhr_p_2a": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "rhr_v_42a": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "rhr_v_53a": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "rhr_v_48a": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "rhr_v_3a": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "rhr_v_64a": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "rhr_v_64b": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "rhr_v_64c": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "rhr_v_4a": {
        "positions": {
			0: 45,
			1: -45,
		},
        "position": 0,
        "lights" : {
            "green" : True,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "rhr_v_6a": {
        "positions": {
			0: 45,
			1: -45,
		},
        "position": 0,
        "lights" : {
            "green" : True,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },

    #MSIVs (inboard)
    "ms_v_22a": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_v_22b": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_v_22c": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_v_22d": {
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
        "flag" : "green",
        "momentary" : False,
    },

    #MSIVs (outboard)
    "ms_v_28a": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_v_28b": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_v_28c": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "ms_v_28d": {
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
        "flag" : "green",
        "momentary" : False,
    },


    #P800 (BD. C)

    "cb_s1": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
            "sync" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_s2": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
            "sync" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_s3": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
            "sync" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },

    "cb_s5": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
            "sync" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_s6": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
            "sync" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },

    #SL-11
    "cb_1_11": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_11_1": {
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
        "flag" : "green",
        "momentary" : False,
    },
    #SL-21
    "cb_2_21": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_21_2": {
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
        "flag" : "green",
        "momentary" : False,
    },
    #SL-31
    "cb_3_31": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_31_3": {
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
        "flag" : "green",
        "momentary" : False,
    },

    "cb_2_4": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
            "sync" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_4_2": {
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
        "flag" : "green",
        "momentary" : False,
    },

    "cb_7_1": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
            "sync" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "sync_cb_7_1": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },
    "cb_1_7": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_8_3": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
            "sync" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "sync_cb_8_3": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },
    "cb_3_8": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
        },
        "flag" : "green",
        "momentary" : False,
    },

    #TR-B to SM-7

    "cb_b7": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
            "sync" : False,
            "xfer" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "sync_cb_b7": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },

    #TR-B to SM-8

    "cb_b8": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
            "sync" : False,
            "xfer" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "sync_cb_b8": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },

    #DG1
    "cb_dg1_7": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "close_permit" : True,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_7dg1": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "dg1_voltreg": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },
    "cb_dg1_7_mode": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },
    "sync_cb_dg1_7": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },
    "dg1_gov": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },
    "diesel_gen_1": {
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
        "flag" : "green",
        "momentary" : False,
    },

    #DG2
    "cb_dg2_8": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "close_permit" : True,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_8dg2": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : True,
            "red" : False,
            "lockout" : True,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "dg2_voltreg": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },
    "cb_dg2_8_mode": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },
    "sync_cb_dg2_8": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },
    "dg2_gov": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },
    "diesel_gen_2": {
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
        "flag" : "green",
        "momentary" : False,
    },

    #SM-7 loads

    "cb_7_73": {
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
        "flag" : "green",
        "momentary" : True,
    },

    #SM-8 loads

    "cb_8_83": {
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
        "flag" : "green",
        "momentary" : True,
    },



    "cb_4885": {
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
        "flag" : "green",
        "momentary" : False,
    },
    "cb_4888": {
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
        "flag" : "green",
        "momentary" : False,
    },

    "sync_cb_4885": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },
    "sync_cb_4888": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },



    #Reactor Recirculation

    #RR B
    "cb_rrb": {
        "positions": {
            -1: 90,
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
            "lockout" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_rpt_3b": {
        "positions": {
            -1: 90,
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_rpt_4b": {
        "positions": {
            -1: 90,
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },

    #RR A
    "cb_rra": {
        "positions": {
            -1: 90,
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
            "lockout" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_rpt_3a": {
        "positions": {
            -1: 90,
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cb_rpt_4a": {
        "positions": {
            -1: 90,
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },


    #Condenser Vacuum Control (AR)

    "ar_p_1a": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "ar_p_1b": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },

    #Condensate

    "cond_p_1a": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cond_p_1b": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },
    "cond_p_1c": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },

    "cond_p_2a": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
            "lockout" : True,
        },
        "flag" : "green",
        "momentary" : True,
    },
    "cond_p_2b": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
            "lockout" : True,
        },
        "flag" : "green",
        "momentary" : True,
    },
    "cond_p_2c": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
            "lockout" : True,
        },
        "flag" : "green",
        "momentary" : True,
    },

    #RFT
    "ms_v_105a": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : True,
    },
    "ms_v_105b": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : True,
    },

    "rfw_v_102a": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : True,
    },
    "rfw_v_102b": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : True,
    },

    "rft_dt_1a_trip": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "tripckt" : True,
        },
        "flag" : "green",
        "momentary" : True,
    },
    "rft_tng_1a": {
        "positions": {
			0: 0,
			1: -45,
		},
        "position": 0,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },

    "rft_dt_1b_trip": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "tripckt" : True,
        },
        "flag" : "green",
        "momentary" : True,
    },
    "rft_tng_1b": {
        "positions": {
			0: 0,
			1: -45,
		},
        "position": 0,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : False,
    },

    #CRD system
    "crd_p_1a": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : True,
    },
    "crd_p_1b": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : True,
    },
    "crd_v_3": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : True,
    },

    "sw_p_1a": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : True,
    },
    "sw_v_2a": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : True,
    },
    "rhr_v_68a": {
        "positions": {
			0: 45,
			1: 0,
			2: -45,
		},
        "position": 1,
        "lights" : {
            "green" : False,
            "red" : False,
        },
        "flag" : "green",
        "momentary" : True,
    },


    #RPS/A Backpanel
    "msiv_a_cond_vac": {
        "positions": {
			0: 45,
			1: -45,
		},
        "position": 0,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
    },
    "msiv_a_rpvl_stm": {
        "positions": {
			0: 45,
			1: -45,
		},
        "position": 0,
        "lights" : {},
        "flag" : "green",
        "momentary" : False,
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

    "rcic_flow" : 0,

    "rcic_rpm" : 0,

    "rcic_supply_press" : 0,
    "rcic_exhaust_press" : 0,

    "rcic_pump_suct_press" : 0,
    "rcic_pump_disch_press" : 0,

    "lpcs_flow" : 0,
    "lpcs_press" : 0,

    "rhr_a_flow" : 0,
    "rhr_a_press" : 0,

    "bus_4_voltage" : 4160,
    "main_generator_sync" : 0,
    "div_1_sync" : 0,
    "div_2_sync" : 0,

    #Reactor Recirculation

    #RR B

    "rrc_p_1b_volts" : 0,
    "rrc_p_1b_amps" : 0,
    "rrc_p_1b_freq" : 0,
    "rrc_p_1b_speed" : 0,

    "station_1b_flow" : 0,
    "station_1b_bias" : 0,
    "station_1b_demand" : 0,
    "station_1b_actual" : 0,

    #RR A

    "rrc_p_1a_volts" : 0,
    "rrc_p_1a_amps" : 0,
    "rrc_p_1a_freq" : 0,
    "rrc_p_1a_speed" : 0,

    "station_1a_flow" : 0,
    "station_1a_bias" : 0,
    "station_1a_demand" : 0,
    "station_1a_actual" : 0,

    "rwm_group" : -1,
    "rwm_insert_error_1" : -1,
    "rwm_insert_error_2" : -1,
    "rwm_withdraw_error" : -1,


    #EHC
    "mt_rpm" : 0,

    #Condensate
    "cond_booster_discharge_press" : 0,
    "cond_booster_discharge_temp" : 0,
    "cond_p_2a_amps" : 0,
    "cond_p_2b_amps" : 0,
    "cond_p_2c_amps" : 0,

    "cond_discharge_press" : 0,
    "cond_discharge_temp" : 0,
    "cond_p_1a_amps" : 0,
    "cond_p_1b_amps" : 0,
    "cond_p_1c_amps" : 0,

    "rft_dt_1a_rpm" : 0,
    "rft_dt_1b_rpm" : 0,

    "rfw_rpv_inlet_pressure" : 0,

    "crd_p_1a_amps" : 0,
    "crd_p_1b_amps" : 0,

    "charge_header_pressure" : 0,
    "drive_header_flow" : 0,
    "cooling_header_flow" : 0,

    "drive_header_dp" : 0,
    "cooling_header_dp" : 0,

    "crd_system_flow" : 0,

    "sw_a_flow" : 0,
    "sw_a_press" : 0,
    "sw_a_temp" : 0,
    "sw_p_1a_amps" : 0,
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
    "RMCS_SELECT_BLOCK": False,
    #Rod Motion Controls
    "RMCS_SETTLE": False,
    "RMCS_INSERT": False,
    "RMCS_WITHDRAW": False,
    "RMCS_CONT_WITHDRAW": False,

    "cr_light_normal_1": True,
    "cr_light_normal_2": True,
    "cr_light_normal_3": True,
    "cr_light_normal_4": True,
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
    "hpcs_l8": False,


    # SRMs

    "SELECT_SRM_A": False,
    "SRM_A_POS_IN": False,
    "SRM_A_POS_OUT": False,
    "SRM_A_RETRACT_PERMIT": False,

    "SELECT_SRM_B": False,
    "SRM_B_POS_IN": False,
    "SRM_B_POS_OUT": False,
    "SRM_B_RETRACT_PERMIT": False,

    "SELECT_SRM_C": False,
    "SRM_C_POS_IN": False,
    "SRM_C_POS_OUT": False,
    "SRM_C_RETRACT_PERMIT": False,

    "SELECT_SRM_D": False,
    "SRM_D_POS_IN": False,
    "SRM_D_POS_OUT": False,
    "SRM_D_RETRACT_PERMIT": False,
    
    # IRMs

    "SELECT_IRM_A": False,
    "IRM_A_POS_IN": False,
    "IRM_A_POS_OUT": False,
    "IRM_A_RETRACT_PERMIT": False,

    "SELECT_IRM_B": False,
    "IRM_B_POS_IN": False,
    "IRM_B_POS_OUT": False,
    "IRM_B_RETRACT_PERMIT": False,

    "SELECT_IRM_C": False,
    "IRM_C_POS_IN": False,
    "IRM_C_POS_OUT": False,
    "IRM_C_RETRACT_PERMIT": False,

    "SELECT_IRM_D": False,
    "IRM_D_POS_IN": False,
    "IRM_D_POS_OUT": False,
    "IRM_D_RETRACT_PERMIT": False,

    "SELECT_IRM_E": False,
    "IRM_E_POS_IN": False,
    "IRM_E_POS_OUT": False,
    "IRM_E_RETRACT_PERMIT": False,

    "SELECT_IRM_F": False,
    "IRM_F_POS_IN": False,
    "IRM_F_POS_OUT": False,
    "IRM_F_RETRACT_PERMIT": False,

    "SELECT_IRM_G": False,
    "IRM_G_POS_IN": False,
    "IRM_G_POS_OUT": False,
    "IRM_G_RETRACT_PERMIT": False,

    "SELECT_IRM_H": False,
    "IRM_H_POS_IN": False,
    "IRM_H_POS_OUT": False,
    "IRM_H_RETRACT_PERMIT": False,

    "DET_DRIVE_IN": False,
    "DET_DRIVE_OUT": False,



    "FCD_OPERATE": True,
    "CHART_RECORDERS_OPERATE": False,

    "rcic_init": False,

    "lpcs_init": False,
    "rhr_cb_init": False,

    "rwm_insert_block": False,
    "rwm_withdraw_block": False,
    "rwm_select_error": False,
    "rwm_manual": False,
    "rwm_auto": False,

    "rwm_seq": False,
    "rwm_init": False,
    "rwm_lpsp": False,
    "rwm_lpap": False,
    "rwm_test": False,
    "rwm_select": False,
    "rwm_diag": False,
    "rwm_rwm": False,
    "rwm_comp": False,
    "rwm_prog": False,

    "ehc_closed": True,
    "ehc_100": False,
    "ehc_500": False,
    "ehc_1500": False,
    "ehc_1800": False,
    "ehc_overspeed": False,

    "ehc_slow": True,
    "ehc_med": False,
    "ehc_fast": False,

    "ehc_line_speed_off": False,
    "ehc_line_speed_selected": False,
    "ehc_line_speed_operating": False,

    "mt_tripped": False,
	"mt_reset": False,
	
	#mech trip test
	"mech_trip_normal": False,
	"mech_trip_lockout": False,
	"mech_trip_oiltrip": False,
	"mech_trip_reset_pb": False,
	
	#mech trip
	"mech_trip_tripped": False,
	"mech_trip_resetting": False,
	"mech_trip_reset": False,
	
	#condenser vacuum trip
	"vacuum_tripped": False,
	"vacuum_normal": False,
	"vacuum_reset": False,
	"vacuum_low": False,
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

    "ALARM_ACK_2": {
        "state" : False,
        "armed" : False,
    },
    "ALARM_RESET_2": {
        "state" : False,
        "armed" : False,
    },

    "ALARM_ACK_3": {
        "state" : False,
        "armed" : False,
    },
    "ALARM_RESET_3": {
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
    "RMCS_CONT_INSERT_PB": {
        "state" : False,
        "armed" : False,
    },
    "RMCS_CONT_WITHDRAW_PB": {
        "state" : False,
        "armed" : False,
    },

    "hpcs_init": {
        "state" : False,
        "armed" : False,
    },
    "hpcs_init_reset": {
        "state" : False,
        "armed" : False,
    },
    "hpcs_l8_reset": {
        "state" : False,
        "armed" : False,
    },

    "SELECT_SRM_A": {
        "state" : False,
        "armed" : False,
    },
    "SELECT_SRM_B": {
        "state" : False,
        "armed" : False,
    },
    "SELECT_SRM_C": {
        "state" : False,
        "armed" : False,
    },
    "SELECT_SRM_D": {
        "state" : False,
        "armed" : False,
    },
    "SELECT_IRM_A": {
        "state" : False,
        "armed" : False,
    },
    "SELECT_IRM_B": {
        "state" : False,
        "armed" : False,
    },
    "SELECT_IRM_C": {
        "state" : False,
        "armed" : False,
    },
    "SELECT_IRM_D": {
        "state" : False,
        "armed" : False,
    },
    "SELECT_IRM_E": {
        "state" : False,
        "armed" : False,
    },
    "SELECT_IRM_F": {
        "state" : False,
        "armed" : False,
    },
    "SELECT_IRM_G": {
        "state" : False,
        "armed" : False,
    },
    "SELECT_IRM_H": {
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

    "rcic_init": {
        "state" : False,
        "armed" : False,
    },
    "rcic_init_reset": {
        "state" : False,
        "armed" : False,
    },

    "lpcs_man_init": {
        "state" : False,
        "armed" : False,
    },
    "lpcs_init_reset": {
        "state" : False,
        "armed" : False,
    },
    "rhr_cb_init": {
        "state" : False,
        "armed" : False,
    },
    "rhr_cb_init_reset": {
        "state" : False,
        "armed" : False,
    },

    #MSIV logic
    "msiv_logic_a": {
        "state" : False,
        "armed" : False,
    },
    "msiv_logic_b": {
        "state" : False,
        "armed" : False,
    },
    "msiv_logic_c": {
        "state" : False,
        "armed" : False,
    },
    "msiv_logic_d": {
        "state" : False,
        "armed" : False,
    },

    "isol_logic_reset_1": {
        "state" : False,
        "armed" : False,
    },
    "isol_logic_reset_2": {
        "state" : False,
        "armed" : False,
    },

    "rrc_a_start": {
        "state" : False,
        "armed" : False,
    },
    "rrc_b_start": {
        "state" : False,
        "armed" : False,
    },

    "station_1a_man": {
        "state" : False,
        "armed" : False,
    },
    "station_1a_auto": {
        "state" : False,
        "armed" : False,
    },
    "station_1a_lower": {
        "state" : False,
        "armed" : False,
    },
    "station_1a_raise": {
        "state" : False,
        "armed" : False,
    },

    "station_1b_man": {
        "state" : False,
        "armed" : False,
    },
    "station_1b_auto": {
        "state" : False,
        "armed" : False,
    },
    "station_1b_lower": {
        "state" : False,
        "armed" : False,
    },
    "station_1b_raise": {
        "state" : False,
        "armed" : False,
    },

    "rwm_seq": {
        "state" : False,
        "armed" : False,
    },
    "rwm_rwm_comp_prog": {
        "state" : False,
        "armed" : False,
    },
    "rwm_diag": {
        "state" : False,
        "armed" : False,
    },
    "rwm_test": {
        "state" : False,
        "armed" : False,
    },

    "ehc_lamp_test": {
        "state" : False,
        "armed" : False,
    },

    "ehc_closed": {
        "state" : False,
        "armed" : False,
    },
    "ehc_100": {
        "state" : False,
        "armed" : False,
    },
    "ehc_500": {
        "state" : False,
        "armed" : False,
    },
    "ehc_1500": {
        "state" : False,
        "armed" : False,
    },
    "ehc_1800": {
        "state" : False,
        "armed" : False,
    },
    "ehc_overspeed": {
        "state" : False,
        "armed" : False,
    },

    "ehc_slow": {
        "state" : False,
        "armed" : False,
    },
    "ehc_med": {
        "state" : False,
        "armed" : False,
    },
    "ehc_fast": {
        "state" : False,
        "armed" : False,
    },

    "ehc_line_speed_off": {
        "state" : False,
        "armed" : False,
    },
    "ehc_line_speed_selected": {
        "state" : False,
        "armed" : False,
    },

    "mt_trip_1": {
        "state" : False,
        "armed" : False,
    },
    "mt_reset_pb": {
        "state" : False,
        "armed" : False,
    },

    "mech_trip_normal": {
        "state" : False,
        "armed" : False,
    },
    "mech_trip_lockout": {
        "state" : False,
        "armed" : False,
    },
    "mech_trip_oiltrip": {
        "state" : False,
        "armed" : False,
    },
    "mech_trip_reset_pb": {
        "state" : False,
        "armed" : False,
    },
}

from simulation.models.control_room_columbia.general_physics import pump

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
        "type" : pump.PumpTypes.Type1,
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
        "type" : pump.PumpTypes.Type1,
    },

    "lpcs_p_1" : {
        "motor_breaker_closed" : False,
        "motor_control_switch" : "lpcs_p_1",
        "bus" : "7",
        "horsepower" : 1000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 250,
        "flow_from_rpm" : 0,
        "rated_flow" : 10000,
        "npshr" : 11,
        "header" : "lpcs_discharge_header",
        "suct_header" : "lpcs_suction_header",
        "type" : pump.PumpTypes.Type1,
    },

    "rhr_p_2a" : {
        "motor_breaker_closed" : False,
        "motor_control_switch" : "rhr_p_2a",
        "bus" : "7",
        "horsepower" : 1000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 250,
        "flow_from_rpm" : 0,
        "rated_flow" : 10000,
        "npshr" : 11,
        "header" : "rhr_a_discharge_header",
        "suct_header" : "rhr_a_suction_header",
        "type" : pump.PumpTypes.Type1,
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
        "npshr" : 11,
        "header" : "rhr_b_discharge_header",
        "suct_header" : "rhr_b_suction_header",
        "type" : pump.PumpTypes.Type1,
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
        "npshr" : 11,
        "header" : "rhr_c_discharge_header",
        "suct_header" : "rhr_c_suction_header",
        "type" : pump.PumpTypes.Type1,
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
        "type" : pump.PumpTypes.Type1,
    },

    "rrc_p_1b" : {
        "motor_breaker_closed" : True,
        "motor_control_switch" : "",
        "bus" : "asdb",
        "horsepower" : 8000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 1500,
        "flow_from_rpm" : 0,
        "rated_flow" : 50000,
        "header" : "",
        "suct_header" : "",
        "custom" : True,
        "type" : pump.PumpTypes.Type1,
    },
    "rrc_p_1a" : {
        "motor_breaker_closed" : True,
        "motor_control_switch" : "",
        "bus" : "asda",
        "horsepower" : 8000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 1500,
        "flow_from_rpm" : 0,
        "rated_flow" : 50000,
        "header" : "",
        "suct_header" : "",
        "custom" : True,
        "type" : pump.PumpTypes.Type1,
    },

    #Main Condenser
    "ar_p_1a" : { #TODO: Need accurate numbers here
        "motor_breaker_closed" : True,
        "motor_control_switch" : "ar_p_1a",
        "bus" : "31", #TODO: Put on MC-3C
        "horsepower" : 1000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 20,
        "flow_from_rpm" : 0,
        "rated_flow" : 100,
        "header" : "",
        "suct_header" : "",
        "custom" : True,
        "type" : pump.PumpTypes.Type1,
    },
    "ar_p_1b" : { #TODO: Need accurate numbers here
        "motor_breaker_closed" : True,
        "motor_control_switch" : "ar_p_1b",
        "bus" : "21", #TODO: Put on MC-2D
        "horsepower" : 1000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 20,
        "flow_from_rpm" : 0,
        "rated_flow" : 100,
        "header" : "",
        "suct_header" : "",
        "custom" : True,
        "type" : pump.PumpTypes.Type1,
    },


    #Condensate

    "cond_p_1a" : {
        "motor_breaker_closed" : True,
        "motor_control_switch" : "cond_p_1a",
        "bus" : "1",
        "horsepower" : 1250,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 200,
        "flow_from_rpm" : 0,
        "rated_flow" : 11000,
        "header" : "condensate_discharge",
        "suct_header" : "condensate_suction",
        "type" : pump.PumpTypes.Type1,
    },
    "cond_p_1b" : {
        "motor_breaker_closed" : True,
        "motor_control_switch" : "cond_p_1b",
        "bus" : "2",
        "horsepower" : 1250,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 200,
        "flow_from_rpm" : 0,
        "rated_flow" : 11000,
        "header" : "condensate_discharge",
        "suct_header" : "condensate_suction",
        "type" : pump.PumpTypes.Type1,
    },
    "cond_p_1c" : {
        "motor_breaker_closed" : True,
        "motor_control_switch" : "cond_p_1c",
        "bus" : "3",
        "horsepower" : 1250,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 200,
        "flow_from_rpm" : 0,
        "rated_flow" : 11000,
        "header" : "condensate_discharge",
        "suct_header" : "condensate_suction",
        "type" : pump.PumpTypes.Type1,
    },

    "cond_p_2a" : {
        "motor_breaker_closed" : True,
        "motor_control_switch" : "cond_p_2a",
        "bus" : "1",
        "horsepower" : 3000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 550,
        "flow_from_rpm" : 0,
        "rated_flow" : 11030,
        "header" : "condensate_booster_discharge",
        "suct_header" : "condensate_discharge",
        "type" : pump.PumpTypes.Type1,
    },
    "cond_p_2b" : {
        "motor_breaker_closed" : True,
        "motor_control_switch" : "cond_p_2b",
        "bus" : "2",
        "horsepower" : 3000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 550,
        "flow_from_rpm" : 0,
        "rated_flow" : 11030,
        "header" : "condensate_booster_discharge",
        "suct_header" : "condensate_discharge",
        "type" : pump.PumpTypes.Type1,
    },
    "cond_p_2c" : {
        "motor_breaker_closed" : True,
        "motor_control_switch" : "cond_p_2c",
        "bus" : "3",
        "horsepower" : 3000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 550,
        "flow_from_rpm" : 0,
        "rated_flow" : 11030,
        "header" : "condensate_booster_discharge",
        "suct_header" : "condensate_discharge",
        "type" : pump.PumpTypes.Type1,
    },


    "rcic_p_1" : { 
        "turbine" : "rcic_turbine",
        "discharge_press" : 0,
        "flow" : 0,
        "actual_flow" : 0,
        "rated_rpm" : 5000,
        "rated_discharge_press" : 1600,
        "rated_flow" : 625,
        "header" : "rcic_discharge_header",
        "suct_header" : "rcic_suction_header",
        "type" : pump.PumpTypes.Type2,
    },

    #RFW
    "rfw_p_1a" : {
        "motor_breaker_closed" : False,
        "motor_control_switch" : "",
        "bus" : "", 
        "horsepower" : 0,
        "rated_rpm" : 5000,
        "rated_discharge_press" : 1400,
        "flow_from_rpm" : 0,
        "rated_flow" : 18520, #lowering rated flow because its unstable
        "header" : "rfw_discharge",
        "suct_header" : "condensate_booster_discharge",
        "shaft_driven" : True,
        "type" : pump.PumpTypes.Type1,
    },
    "rfw_p_1b" : {
        "motor_breaker_closed" : False,
        "motor_control_switch" : "",
        "bus" : "", 
        "horsepower" : 0,
        "rated_rpm" : 5000,
        "rated_discharge_press" : 1400,
        "flow_from_rpm" : 0,
        "rated_flow" : 18520, #lowering rated flow because its unstable
        "header" : "rfw_discharge",
        "suct_header" : "condensate_booster_discharge",
        "shaft_driven" : True,
        "type" : pump.PumpTypes.Type1,
    },

    "crd_p_1a" : {
        "motor_breaker_closed" : False,
        "motor_control_switch" : "crd_p_1a",
        "bus" : "7",
        "horsepower" : 250,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 1700,
        "flow_from_rpm" : 0,
        "rated_flow" : 200,
        "header" : "crd_discharge",
        "suct_header" : "crd_suction",
        "type" : pump.PumpTypes.Type1,
    },
    "crd_p_1b" : {
        "motor_breaker_closed" : False,
        "motor_control_switch" : "crd_p_1b",
        "bus" : "8",
        "horsepower" : 250,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 1700,
        "flow_from_rpm" : 0,
        "rated_flow" : 200,
        "header" : "crd_discharge",
        "suct_header" : "crd_suction",
        "type" : pump.PumpTypes.Type1,
    },

    #SW
    "sw_p_1a" : {
        "motor_breaker_closed" : False,
        "motor_control_switch" : "sw_p_1a",
        "bus" : "7",
        "horsepower" : 2000,
        "rated_rpm" : 1800,
        "rated_discharge_press" : 250,
        "flow_from_rpm" : 0,
        "rated_flow" : 10000,
        "header" : "sw_p_1a_discharge",
        "suct_header" : "",
        "type" : pump.PumpTypes.Type1,
    },
}

turbines = {
    "rcic_turbine" : {
        "rpm" : 0,
        "rated_rpm" : 6250,
        "flow_to_rpm" : 2.285534715,
        "acceleration_value" : 0.1,
        "trip" : False,
        "mechanical_trip" : False,
        "trip_valve" : "rcic_v_1",
        "steam_flow_valve" : "rcic_v_45",
        "governor_valve" : "rcic_v_2",
    },
}

recorders = {}

rods = {}

reactor_water_temperature = 100

from simulation.models.control_room_columbia.systems import chart
chart.initialize()

ac_power.initialize()

from simulation.models.control_room_columbia import rod_generation
rod_generation.run(rods,buttons)

pump.initialize_pumps()

from simulation.models.control_room_columbia.general_physics import fluid
fluid.initialize_headers()

from simulation.models.control_room_columbia.general_physics import gas
from simulation.models.control_room_columbia.general_physics import turbine
from simulation.models.control_room_columbia.general_physics import turbine_new
turbine.initialize_pumps()
turbine_new.initialize()

from simulation.models.control_room_columbia.general_physics import main_condenser
from simulation.models.control_room_columbia.general_physics import main_turbine
from simulation.models.control_room_columbia.general_physics import main_generator
main_condenser.initalize()


from simulation.models.control_room_columbia.general_physics import diesel_generator
diesel_generator.initialize()

from simulation.models.control_room_columbia.systems import diesels
from simulation.models.control_room_columbia.systems import safety_relief
from simulation.models.control_room_columbia.systems import irm_srm_positioner
from simulation.models.control_room_columbia.systems import condensate
from simulation.models.control_room_columbia.systems import feedwater
from simulation.models.control_room_columbia.systems import rcic
from simulation.models.control_room_columbia.systems import hpcs
from simulation.models.control_room_columbia.systems import lpcs
from simulation.models.control_room_columbia.systems import deh
from simulation.models.control_room_columbia.systems import pcis
from simulation.models.control_room_columbia.systems import rod_worth_minimizer
from simulation.models.control_room_columbia.systems import residual_heat_removal
from simulation.models.control_room_columbia.systems import service_water
from simulation.models.control_room_columbia.systems import sync
from simulation.models.control_room_columbia.systems import loop_sequence
from simulation.models.control_room_columbia.systems import rrc
from simulation.models.control_room_columbia.systems import control_rod_drive
from simulation.models.control_room_columbia.systems import fire
from simulation.models.control_room_columbia.systems import fire_control_panel
control_rod_drive.initialize()
loop_sequence.initialize()
sync.initialize()
deh.initialize()
feedwater.initialize()
fire.initialize()

def model_run_fast(delta):
    fluid.run(delta) 
    gas.run(delta)
    pump.run(delta)
    reactor_inventory.run(delta)

runs = 0
def model_run(delta):
    global runs
    reactor_physics.run(delta,rods)
    chart.run()
    annunciators.run()
    reactor_protection_system.run()
    rod_drive_control_system.run(rods,buttons)
    rod_position_information_system.run(rods,alarms,buttons)
    neutron_monitoring.run(alarms,buttons,indicators,rods,switches,values)
    ac_power.run()
    diesel_generator.run()
    sync.run()
    loop_sequence.run()
    turbine.run() #TODO: Deprecate
    turbine_new.run()
    main_condenser.run()
    main_turbine.run()
    main_generator.run()
    diesels.run()

    residual_heat_removal.run()
    service_water.run()
    rrc.run()
    control_rod_drive.run()
    safety_relief.run()
    irm_srm_positioner.run()
    condensate.run()
    feedwater.run()
    rcic.run()
    hpcs.run()
    lpcs.run()
    deh.run()
    pcis.run()
    rod_worth_minimizer.run()
    fire.run(delta)
    fire_control_panel.run(delta)
    #from simulation.models.control_room_columbia.systems import fukushima
    #fukushima.run(runs)
    runs += 1