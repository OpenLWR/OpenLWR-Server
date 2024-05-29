
from simulation.constants.annunciator_states import AnnunciatorStates
import math

reactor_protection_systems = {
    "A" : {
        "reset_timer" : -1,
        "channel_1_trip" : False,
        "channel_2_trip" : False,
    },
    "B" : {
        "reset_timer" : -1,
        "channel_1_trip" : False,
        "channel_2_trip" : False,
    },
}

rps_alarms = {
    "A" : {
        "RPV Level Low" : "rpv_level_low_trip_a",
        "RPV Press High" : "rpv_press_high_trip_a",
        "Mode Switch In Shutdown" : "mode_switch_in_shutdown_position_a",
        "Neutron Monitor System" : "neutron_monitor_system_trip_a",
    },
    "B" : {
        "RPV Level Low" : "rpv_level_low_trip_b",
        "RPV Press High" : "rpv_press_high_trip_b",
        "Mode Switch In Shutdown" : "mode_switch_in_shutdown_position_b",
        "Neutron Monitor System" : "neutron_monitor_system_trip_b",
    },
}

withdraw_blocks = []

withdraw_block = False
insert_block = False

def run(alarms,buttons,indicators,rods,switches):
    global withdraw_block

    withdraw_block = withdraw_blocks != []


    if switches["reactor_mode_switch"]["position"] == 0:
        add_withdraw_block("Mode_Switch_Shutdown")
    else:
        remove_withdraw_block("Mode_Switch_Shutdown")

    if buttons["SCRAM_A1"]["state"]:
        reactor_protection_systems["A"]["channel_1_trip"] = True
    if buttons["SCRAM_A2"]["state"]:
        reactor_protection_systems["A"]["channel_2_trip"] = True

    if buttons["SCRAM_B1"]["state"]:
        reactor_protection_systems["B"]["channel_1_trip"] = True
    if buttons["SCRAM_B2"]["state"]:
        reactor_protection_systems["B"]["channel_2_trip"] = True

    if buttons["SCRAM_RESET_A"]["state"]:
        if scram_reset_permissive("A"):
            reactor_protection_systems["A"]["channel_1_trip"] = False
            reactor_protection_systems["A"]["channel_2_trip"] = False
            for scram in rps_scram_trips["A"]:
                rps_scram_trips["A"][scram]["sealed_in"] = False

    if buttons["SCRAM_RESET_B"]["state"]:
        if scram_reset_permissive("B"):
            reactor_protection_systems["B"]["channel_1_trip"] = False
            reactor_protection_systems["B"]["channel_2_trip"] = False
            for scram in rps_scram_trips["B"]:
                rps_scram_trips["B"][scram]["sealed_in"] = False


    if reactor_protection_systems["A"]["reset_timer"] == 0 and switches["reactor_mode_switch"]["position"] == 0:
        rps_scram_trips["A"]["Mode Switch In Shutdown"]["bypassed"] = True
    elif reactor_protection_systems["A"]["reset_timer"] == 0 and switches["reactor_mode_switch"]["position"] != 0 :
        rps_scram_trips["A"]["Mode Switch In Shutdown"]["bypassed"] = False

    if reactor_protection_systems["B"]["reset_timer"] == 0 and switches["reactor_mode_switch"]["position"] == 0:
        rps_scram_trips["B"]["Mode Switch In Shutdown"]["bypassed"] = True
    elif reactor_protection_systems["B"]["reset_timer"] == 0 and switches["reactor_mode_switch"]["position"] != 0 :
        rps_scram_trips["B"]["Mode Switch In Shutdown"]["bypassed"] = False

    automatic_scram_signals()

    trip_a = (reactor_protection_systems["A"]["channel_1_trip"] or reactor_protection_systems["A"]["channel_2_trip"])

    trip_b = (reactor_protection_systems["B"]["channel_1_trip"] or reactor_protection_systems["B"]["channel_2_trip"])

    alarms["1/2_scram_system_a"]["alarm"] = trip_a 
    alarms["1/2_scram_system_b"]["alarm"] = trip_b
    alarms["reactor_scram_a1_and_b1_loss"]["alarm"] = reactor_protection_systems["A"]["channel_1_trip"] and reactor_protection_systems["B"]["channel_1_trip"]
    alarms["reactor_scram_a2_and_b2_loss"]["alarm"] = reactor_protection_systems["A"]["channel_2_trip"] and reactor_protection_systems["B"]["channel_2_trip"]

    for reason in rps_scram_trips["A"]:
        alarms[rps_alarms["A"][reason]]["alarm"] = rps_scram_trips["A"][reason]["sealed_in"]

    for reason in rps_scram_trips["B"]:
        alarms[rps_alarms["B"][reason]]["alarm"] = rps_scram_trips["A"][reason]["sealed_in"]



    scram_signal = trip_a and trip_b

    if scram_signal:
        if reactor_protection_systems["A"]["reset_timer"] == -1:
            reactor_protection_systems["A"]["reset_timer"] = 100
        elif reactor_protection_systems["A"]["reset_timer"] > 0:
            reactor_protection_systems["A"]["reset_timer"] -= 1

        if reactor_protection_systems["B"]["reset_timer"] == -1:
            reactor_protection_systems["B"]["reset_timer"] = 100
        elif reactor_protection_systems["B"]["reset_timer"] > 0:
            reactor_protection_systems["B"]["reset_timer"] -= 1

    elif switches["reactor_mode_switch"]["position"] != 0:
        reactor_protection_systems["A"]["reset_timer"] = -1
        reactor_protection_systems["B"]["reset_timer"] = -1

    for rod in rods:
        info = rods[rod] 
        #scram the reactor if both RPS trains are tripped
        if info["scram"] != scram_signal:
            info["scram"] = scram_signal

    #Scram trips

    #indicators for, IE, the RMCS

    indicators["SCRAM_A1"] = not trip_a
    indicators["SCRAM_A2"] = not trip_a
    indicators["SCRAM_A3"] = not trip_a
    indicators["SCRAM_A4"] = not trip_a
    indicators["SCRAM_A5"] = trip_a
    indicators["SCRAM_A6"] = trip_a

    indicators["SCRAM_B1"] = not trip_b
    indicators["SCRAM_B2"] = not trip_b
    indicators["SCRAM_B3"] = not trip_b
    indicators["SCRAM_B4"] = not trip_b
    indicators["SCRAM_B5"] = trip_b
    indicators["SCRAM_B6"] = trip_b
            
    indicators["RMCS_WITHDRAW_BLOCK"] = withdraw_block
    alarms["rod_out_block"]["alarm"] = withdraw_block

def scram(reason):

    print("This system for scramming is deprecated! Please do not use it! This scram has been discarded!")

def scram_reset_permissive(system):
    for scram in rps_scram_trips[system]:
        if rps_scram_trips[system][scram]["active"]:
            return False
        
    return True
    
def add_withdraw_block(reason):
    if not reason in withdraw_blocks:
        withdraw_blocks.append(reason)

def remove_withdraw_block(reason):
    if reason in withdraw_blocks:
        withdraw_blocks.remove(reason)

#Scram trips

def automatic_scram_signals():
    for scram in rps_scram_trips["A"]:

        scram_trip = rps_scram_trips["A"][scram]
        scram_trip["active"] = scram_trip["function"](scram_trip)

        if scram_trip["active"]:
            reactor_protection_systems["A"]["channel_1_trip"] = True
            reactor_protection_systems["A"]["channel_2_trip"] = True
            scram_trip["sealed_in"] = True

    for scram in rps_scram_trips["B"]:

        scram_trip = rps_scram_trips["B"][scram]
        scram_trip["active"] = scram_trip["function"](scram_trip)

        if scram_trip["active"]:
            reactor_protection_systems["B"]["channel_1_trip"] = True
            reactor_protection_systems["B"]["channel_2_trip"] = True
            scram_trip["sealed_in"] = True

def scram_trip_mode_switch_shutdown(info):
    from simulation.models.control_room_columbia import model 
    if (not info["bypassed"]) and model.switches["reactor_mode_switch"]["position"] == 0 :
        return True

    return False

def scram_trip_rpv_press_high(info):
    from simulation.models.control_room_columbia.reactor_physics import pressure 
    if pressure.Pressures["Vessel"]/6895 > 1060:
        return True

    return False

def scram_trip_rpv_level_low(info):
    from simulation.models.control_room_columbia.reactor_physics import reactor_inventory 
    if reactor_inventory.rx_level_wr < 13:
        return True
    
    return False

def scram_trip_neutron_monitor_system(info):
    from simulation.models.control_room_columbia import neutron_monitoring 

    return neutron_monitoring.scram_reactor
    

rps_scram_trips = {
    "A" : {
        "Mode Switch In Shutdown" : {
            "bypassed" : False,
            "sealed_in" : False,
            "active" : False, #Condition still exists (cannot reset)
            "function" : scram_trip_mode_switch_shutdown,
        },
        "RPV Level Low" : {
            "bypassed" : False,
            "sealed_in" : False,
            "active" : False, 
            "function" : scram_trip_rpv_level_low,
        },
        "RPV Press High" : {
            "bypassed" : False,
            "sealed_in" : False,
            "active" : False, 
            "function" : scram_trip_rpv_press_high,
        },
        "Neutron Monitor System" : {
            "bypassed" : False,
            "sealed_in" : False,
            "active" : False, 
            "function" : scram_trip_neutron_monitor_system,
        },
    },
    "B" : {
        "Mode Switch In Shutdown" : {
            "bypassed" : False,
            "sealed_in" : False,
            "active" : False, 
            "function" : scram_trip_mode_switch_shutdown,
        },
        "RPV Level Low" : {
            "bypassed" : False,
            "sealed_in" : False,
            "active" : False, 
            "function" : scram_trip_rpv_level_low,
        },
        "RPV Press High" : {
            "bypassed" : False,
            "sealed_in" : False,
            "active" : False, 
            "function" : scram_trip_rpv_press_high,
        },
        "Neutron Monitor System" : {
            "bypassed" : False,
            "sealed_in" : False,
            "active" : False, 
            "function" : scram_trip_neutron_monitor_system,
        },
    },
}