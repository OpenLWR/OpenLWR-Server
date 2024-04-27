
from simulation.constants.annunciator_states import AnnunciatorStates
import math

rps_a_trip = False
rps_b_trip = False

def run(alarms,buttons,indicators,rods,switches):
    global rps_a_trip
    global rps_b_trip
    if switches["reactor_mode_switch"]["position"] == 0:
        rps_a_trip = True
        rps_b_trip = True

    if buttons["SCRAM_A1"] or buttons["SCRAM_A2"]:
        rps_a_trip = True
    if buttons["SCRAM_B1"] or buttons["SCRAM_B2"]:
        rps_b_trip = True
    if rps_a_trip:
        alarms["rps_a_auto_trip"]["alarm"] = True
        indicators["SCRAM_SOLENOID_A"] = False
        indicators["SCRAM_SOLENOID_C"] = False
        indicators["SCRAM_SOLENOID_E"] = False
        indicators["SCRAM_SOLENOID_G"] = False
    if rps_b_trip:
        alarms["rps_b_auto_trip"]["alarm"] = True
        indicators["SCRAM_SOLENOID_B"] = False
        indicators["SCRAM_SOLENOID_D"] = False
        indicators["SCRAM_SOLENOID_F"] = False
        indicators["SCRAM_SOLENOID_H"] = False
    for rod in rods:
        info = rods[rod] 
        #scram the reactor if both RPS trains are tripped
        if info["scram"] != (rps_a_trip and rps_b_trip):
            info["scram"] = (rps_a_trip and rps_b_trip)
