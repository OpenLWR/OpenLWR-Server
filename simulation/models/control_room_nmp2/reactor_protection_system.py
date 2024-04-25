
from simulation.constants.annunciator_states import AnnunciatorStates
import math

rps_a_trip = False
rps_b_trip = False

def run(alarms,buttons):
    global test_value
    print(buttons)
    if buttons["SCRAM_A1"]:
        rps_a_trip = True
    if buttons["SCRAM_B1"]:
        rps_b_trip = True
    if rps_a_trip:
        alarms["rps_a_auto_trip"] = AnnunciatorStates.ACTIVE
    if rps_b_trip:
        alarms["rps_b_auto_trip"] = AnnunciatorStates.ACTIVE
