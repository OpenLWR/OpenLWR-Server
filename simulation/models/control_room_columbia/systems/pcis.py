from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.reactor_physics import pressure
from simulation.models.control_room_columbia.general_physics import fluid
from simulation.models.control_room_columbia.general_physics import ac_power
from simulation.models.control_room_columbia.systems import residual_heat_removal
from simulation.models.control_room_columbia.general_physics import main_condenser

isolation_groups = {
    "1" : { #Main isolation group. MSIVs, MSL drains
        "ms_v_22a",
        "ms_v_22b",
        "ms_v_22c",
        "ms_v_22d",
        "ms_v_28a",
        "ms_v_28b",
        "ms_v_28c",
        "ms_v_28d",

        #MSLD
        "ms_v_67a",
        "ms_v_67b",
        "ms_v_67c",
        "ms_v_67d",
        "ms_v_16",
        "ms_v_19",

    }, 
    "2" : { #Reactor Water Sample
        "rrc_v_19",
        "rrc_v_20",
    }, 
    "3" : { #Containment exhaust & supply purge

    }, 
    "4" : { #Typical FAZ signal. Has TIP and EDR/FDR isolations.

    }, 
    "6" : { #RHR System & LPCI

    }, 
    "7" : { #RWCU System

    }, 
    "8" : { #RCIC System

    }, 
    "10" : { #I dunno what this is

    }, 
    "11" : { #I dunno what this is

    }, 
}

isolation_signals = {
    "A" : { #RPV Level 2
        "signal" : False,
        "seal_in" : False,
        "alarm" : "nssss_isol_rpv_level_low",
    },
    "C" : { #Main Steam Line - Radiation High
        "signal" : False,
        "seal_in" : False,
    },
    "D" : { #Main Steam Line - Leak Det (Tunnel high temp, high delta T or high flow)
        "signal" : False,
        "seal_in" : False,
    },
    "E" : { #RWCU high diff flow or high blowdown flow
        "signal" : False,
        "seal_in" : False,
    },
    "F" : { #High Drywell Pressure
        "signal" : False,
        "seal_in" : False,
    },
    "G" : { #Low Condenser Vacuum
        "signal" : False,
        "seal_in" : False,
    },
    "J" : { #RWCU system - Leak Det (high area temperature or high delta T)
        "signal" : False,
        "seal_in" : False,
    },
    "K" : { #RCIC System - Leak Det (high area temperature, high delta T, or high steam flow) NOTE: Low Steam Pressure and Turb Exhaust Diaph high press are not a part of the PCRVIS
        "signal" : False,
        "seal_in" : False,
    },
    "L" : { #RPV Level 3
        "signal" : False,
        "seal_in" : False,
    },
    "M" : { #RHR SDC System - High Suction Flow
        "signal" : False,
        "seal_in" : False,
    },
    "P" : { #Main Steam Line Pressure - Low (At turbine inlet) * RMS in RUN
        "signal" : False,
        "seal_in" : False,
    },
    "R" : { #RHR System - Leak Det (High area temperature or high delta T)
        "signal" : False,
        "seal_in" : False,
    },
    "U" : { #High Reactor Pressure (SDC Isolation)
        "signal" : False,
        "seal_in" : False,
    },
    "V" : { #RPV Level 1
        "signal" : False,
        "seal_in" : False,
        "alarm" : "ns4_group_1_isol_rpv_level_low",
    },
    "W" : { #High Temp at outlet of RWCU HX
        "signal" : False,
        "seal_in" : False,
    },
    "Y" : { #SLC Actuated
        "signal" : False,
        "seal_in" : False,
    },
    "Z" : { #Reactor building ventilation exhaust plenum high radiation
        "signal" : False,
        "seal_in" : False,
    },
}

logic = {
    "A" : False,
    "B" : False,
    "C" : False,
    "D" : False,
}

def run():
    system_a = False
    system_b = False

    #This is all kind of a mess

    #TODO: use the actual RPS bus and whatnot
    low_pressure = bool(pressure.Pressures["Vessel"]/6895 < 835)
    model.alarms["main_steam_line_press_low"]["alarm"] = low_pressure

    if low_pressure and model.switches["reactor_mode_switch"]["position"] == 3:
        logic["C"] = True
        logic["D"] = True

    stop_valves_closed = bool(fluid.valves["ms_v_sv1"]["percent_open"] < 90 and fluid.valves["ms_v_sv2"]["percent_open"] < 90 and fluid.valves["ms_v_sv3"]["percent_open"] < 90 and fluid.valves["ms_v_sv4"]["percent_open"] < 90)
    cond_vac_bypassed = bool(model.switches["reactor_mode_switch"]["position"] != 3 and model.switches["msiv_a_cond_vac"]["position"] == 1 and stop_valves_closed and pressure.Pressures["Vessel"]/6895 < 1060)

    if main_condenser.MainCondenserBackPressure < 8.5 and not cond_vac_bypassed:
        logic["C"] = True
        logic["D"] = True
        model.alarms["nssss_isol_main_condenser_vac_low_a"]["alarm"] = True
        model.alarms["nssss_isol_main_condenser_vac_low_b"]["alarm"] = True
    else:
        model.alarms["nssss_isol_main_condenser_vac_low_a"]["alarm"] = False
        model.alarms["nssss_isol_main_condenser_vac_low_b"]["alarm"] = False

    model.alarms["nssss_main_condsr_vac_low_bypass_a"]["alarm"] = cond_vac_bypassed
    model.alarms["nssss_main_condsr_vac_low_bypass_b"]["alarm"] = cond_vac_bypassed

    low_rpv_lvl_bypassed = model.switches["msiv_a_rpvl_stm"]["position"] == 1

    if reactor_inventory.rx_level_wr <= -129 and not low_rpv_lvl_bypassed:
        logic["C"] = True
        logic["D"] = True
        model.alarms["nssss_isol_rpv_level_low_a"]["alarm"] = True
        model.alarms["nssss_isol_rpv_level_low_b"]["alarm"] = True
    else:
        model.alarms["nssss_isol_rpv_level_low_a"]["alarm"] = False
        model.alarms["nssss_isol_rpv_level_low_b"]["alarm"] = False

    model.alarms["msiv_isol_sys_a_lvl/tmp_bypass"]["alarm"] = low_rpv_lvl_bypassed
    model.alarms["msiv_isol_sys_b_lvl/tmp_bypass"]["alarm"] = low_rpv_lvl_bypassed


    #RPS A Powers A/C, so no isolations would result from a loss of RPS A.
    if not ac_power.busses["7"].is_voltage_at_bus(4000):
        logic["A"] = True
        logic["C"] = True

    #an inboard and outboard isolation except MSIVs would result from a loss of RPS B
    if not ac_power.busses["8"].is_voltage_at_bus(4000):
        logic["B"] = True
        logic["D"] = True

    #TODO: check if the logic is allowed to be reset at this time
    if model.buttons["isol_logic_reset_1"]["state"]:
        logic["A"] = False
        logic["B"] = False

    if model.buttons["isol_logic_reset_2"]["state"]:
        logic["C"] = False
        logic["D"] = False

    if model.buttons["msiv_logic_a"]["state"]:
        logic["A"] = True

    if model.buttons["msiv_logic_b"]["state"]:
        logic["B"] = True

    if model.buttons["msiv_logic_c"]["state"]:
        logic["C"] = True

    if model.buttons["msiv_logic_d"]["state"]:
        logic["D"] = True

    if logic["A"] or logic["C"]: #half MSIV trip
        system_a = True
        model.alarms["msiv_half_trip_system_a"]["alarm"] = True

    if logic["B"] or logic["D"]:
        system_b = True
        model.alarms["msiv_half_trip_system_b"]["alarm"] = True

    if logic["B"]: #Outboard P601 Valve isolation
        model.alarms["rc_1_half_trip"]["alarm"] = True

    if logic["D"]: #Inboard P601 Valve Isolation
        model.alarms["rc_2_half_trip"]["alarm"] = True

    if system_a and system_b:
        #MSIV Closure occurs
        for msiv in {"ms_v_22a","ms_v_22b","ms_v_22c","ms_v_22d","ms_v_28a","ms_v_28b","ms_v_28c","ms_v_28d"}:
            fluid.valves[msiv]["sealed_in"] = False

