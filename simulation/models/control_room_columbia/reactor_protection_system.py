
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

    if buttons["SCRAM_A1"]:
        reactor_protection_systems["A"]["channel_1_trip"] = True
    if buttons["SCRAM_A2"]:
        reactor_protection_systems["A"]["channel_2_trip"] = True

    if buttons["SCRAM_B1"]:
        reactor_protection_systems["B"]["channel_1_trip"] = True
    if buttons["SCRAM_B2"]:
        reactor_protection_systems["B"]["channel_2_trip"] = True

    if buttons["SCRAM_RESET_A"]:
        reactor_protection_systems["A"]["channel_1_trip"] = False
        reactor_protection_systems["A"]["channel_2_trip"] = False

    if buttons["SCRAM_RESET_B"]:
        reactor_protection_systems["B"]["channel_1_trip"] = False
        reactor_protection_systems["B"]["channel_2_trip"] = False
    
    if reactor_protection_systems["A"]["channel_1_trip"] or reactor_protection_systems["A"]["channel_2_trip"]:
        alarms["rps_a_auto_trip"]["alarm"] = True
    if reactor_protection_systems["B"]["channel_1_trip"] or reactor_protection_systems["B"]["channel_2_trip"]:
        alarms["rps_b_auto_trip"]["alarm"] = True

    trip_a = (reactor_protection_systems["A"]["channel_1_trip"] or reactor_protection_systems["A"]["channel_2_trip"])

    trip_b = (reactor_protection_systems["B"]["channel_1_trip"] or reactor_protection_systems["B"]["channel_2_trip"])

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
    from simulation.models.control_room_columbia.reactor_physics.reactor_inventory import rx_level_wr
    if rx_level_wr < 13:
        scram("RPV Level low")

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
    alarms["control_rod_out_block"]["alarm"] = withdraw_block

def scram(reason):
    #TODO: RPS Fail to trip, RPS trip reasons
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