from simulation.constants.annunciator_states import AnnunciatorStates
from simulation.models.control_room_nmp2 import annunciators
from simulation.models.control_room_nmp2 import reactor_protection_system
import math

alarms = {
    "rps_a_auto_trip" : AnnunciatorStates.CLEAR,
    "rps_b_auto_trip" : AnnunciatorStates.CLEAR,
}

switches = {}

values = {}

indicators = {}

buttons = {
    "SCRAM_A1": False,
    "SCRAM_B1": False,
}

def model_run():
    print(buttons)
    #TODO: import reactor protection system and annunciator logic, and run them here
    annunciators.run(alarms)
    reactor_protection_system.run(alarms,buttons)