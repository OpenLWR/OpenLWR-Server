from simulation.constants.annunciator_states import AnnunciatorStates
from simulation.models.control_room_nmp2 import annunciators
from simulation.models.control_room_nmp2 import reactor_protection_system
import math

alarms = {
    "rps_a_auto_trip" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
    "rps_b_auto_trip" : {
        "alarm" : False,
        "state" : AnnunciatorStates.CLEAR,
        "group" : "1",
        "silenced" : False,
    },
}

switches = {}

values = {}

indicators = {
    "SCRAM_SOLENOID_A": True,
    "SCRAM_SOLENOID_B": True,
    "SCRAM_SOLENOID_C": True,
    "SCRAM_SOLENOID_D": True,
    "SCRAM_SOLENOID_E": True,
    "SCRAM_SOLENOID_F": True,
    "SCRAM_SOLENOID_G": True,
    "SCRAM_SOLENOID_H": True,
}

buttons = {
    "SCRAM_A1": False,
    "SCRAM_B1": False,
    "SCRAM_A2": False,
    "SCRAM_B2": False,
    "ALARM_SILENCE_1": False,
    "ALARM_ACK_1": False,
    "ALARM_RESET_1": False,
}

def model_run():
    #TODO: import reactor protection system and annunciator logic, and run them here
    annunciators.run(alarms,buttons)
    reactor_protection_system.run(alarms,buttons,indicators)