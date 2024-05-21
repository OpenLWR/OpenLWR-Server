
from simulation.constants.annunciator_states import AnnunciatorStates
import math

reactor_protection_systems = {
    "A" : {
        "reset_timer" : -1,
        "channel_1_trip" : False,
        "channel_2_trip" : False,
        "reasons" : [] #Trip reasons should match the annunciator name, other than "RPS_A".
        #Ex : "NMS_TRIP"
    },
    "B" : {
        "reset_timer" : -1,
        "channel_1_trip" : False,
        "channel_2_trip" : False,
        "reasons" : [] #Trip reasons should match the annunciator name, other than "RPS_A".
        #Ex : "NMS_TRIP"
    },
}

rps_alarms = {
    "A" : {
        "RPV Level Low" : "rpv_level_low_trip_a",
    },
    "B" : {
        "RPV Level Low" : "rpv_level_low_trip_b",
    },
}

withdraw_blocks = []

withdraw_block = False
insert_block = False

def run(alarms,buttons,indicators,rods,switches):
    global withdraw_block

    withdraw_block = withdraw_blocks != []


    if switches["reactor_mode_switch"]["position"] == 0:
        mode_switch_shutdown()
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
        reactor_protection_systems["A"]["channel_1_trip"] = False
        reactor_protection_systems["A"]["channel_2_trip"] = False

    if buttons["SCRAM_RESET_B"]["state"]:
        reactor_protection_systems["B"]["channel_1_trip"] = False
        reactor_protection_systems["B"]["channel_2_trip"] = False

    trip_a = (reactor_protection_systems["A"]["channel_1_trip"] or reactor_protection_systems["A"]["channel_2_trip"])

    trip_b = (reactor_protection_systems["B"]["channel_1_trip"] or reactor_protection_systems["B"]["channel_2_trip"])

    alarms["1/2_scram_system_a"]["alarm"] = trip_a and not trip_b
    alarms["1/2_scram_system_b"]["alarm"] = trip_b and not trip_a
    alarms["reactor_scram_a1_and_b1_loss"]["alarm"] = reactor_protection_systems["A"]["channel_1_trip"] and reactor_protection_systems["B"]["channel_1_trip"]
    alarms["reactor_scram_a2_and_b2_loss"]["alarm"] = reactor_protection_systems["A"]["channel_2_trip"] and reactor_protection_systems["B"]["channel_2_trip"]

    for reason in rps_alarms["A"]:
        alarms[rps_alarms["A"][reason]]["alarm"] = reason in reactor_protection_systems["A"]["reasons"]

    for reason in rps_alarms["B"]:
        alarms[rps_alarms["B"][reason]]["alarm"] = reason in reactor_protection_systems["B"]["reasons"]



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
    from simulation.models.control_room_columbia.reactor_physics import reactor_inventory 
    if reactor_inventory .rx_level_wr < 13:
        scram("RPV Level Low")

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
    #TODO: RPS Fail to trip, RPS trip reasons
    if reason not in reactor_protection_systems["A"]["reasons"]:
        reactor_protection_systems["A"]["reasons"].append(reason)

    if reason not in reactor_protection_systems["B"]["reasons"]:
        reactor_protection_systems["B"]["reasons"].append(reason)

    reactor_protection_systems["A"]["channel_1_trip"] = True
    reactor_protection_systems["A"]["channel_2_trip"] = True
    reactor_protection_systems["B"]["channel_1_trip"] = True
    reactor_protection_systems["B"]["channel_2_trip"] = True

def mode_switch_shutdown():
    if reactor_protection_systems["A"]["reset_timer"] != 0 or reactor_protection_systems["B"]["reset_timer"] != 0:
        scram("MANUAL")

def add_withdraw_block(reason):
    if not reason in withdraw_blocks:
        withdraw_blocks.append(reason)

def remove_withdraw_block(reason):
    if reason in withdraw_blocks:
        withdraw_blocks.remove(reason)