
from simulation.constants.annunciator_states import AnnunciatorStates
import math

rps_a_trip = False
rps_b_trip = False
withdraw_block = False
insert_block = False

def run(alarms,buttons,indicators,rods,switches):
    global rps_a_trip
    global rps_b_trip
    global withdraw_block
    withdraw_block = False

    if switches["reactor_mode_switch"]["position"] == 0:
        rps_a_trip = True
        rps_b_trip = True
        withdraw_block = True

    if buttons["SCRAM_A1"] or buttons["SCRAM_A2"]:
        rps_a_trip = True
    if buttons["SCRAM_B1"] or buttons["SCRAM_B2"]:
        rps_b_trip = True
    if rps_a_trip:
        alarms["rps_a_auto_trip"]["alarm"] = True
    if rps_b_trip:
        alarms["rps_b_auto_trip"]["alarm"] = True
    for rod in rods:
        info = rods[rod] 
        #scram the reactor if both RPS trains are tripped
        if info["scram"] != (rps_a_trip and rps_b_trip):
            info["scram"] = (rps_a_trip and rps_b_trip)

    #indicators for, IE, the RMCS

    indicators["SCRAM_A1"] = not rps_a_trip
    indicators["SCRAM_A2"] = not rps_a_trip
    indicators["SCRAM_A3"] = not rps_a_trip
    indicators["SCRAM_A4"] = not rps_a_trip
    indicators["SCRAM_A5"] = rps_a_trip
    indicators["SCRAM_A6"] = rps_a_trip

    indicators["SCRAM_B1"] = not rps_b_trip
    indicators["SCRAM_B2"] = not rps_b_trip
    indicators["SCRAM_B3"] = not rps_b_trip
    indicators["SCRAM_B4"] = not rps_b_trip
    indicators["SCRAM_B5"] = rps_b_trip
    indicators["SCRAM_B6"] = rps_b_trip
            
    indicators["RMCS_WITHDRAW_BLOCK"] = withdraw_block
    alarms["control_rod_out_block"]["alarm"] = withdraw_block
