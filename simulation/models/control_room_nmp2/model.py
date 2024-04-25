from simulation.global_variables.values import values
from simulation.global_variables.switches import switches
from simulation.global_variables.alarms import alarms
from simulation.global_variables.indicators import indicators
from simulation.global_variables.buttons import buttons
from simulation.constants.annunciator_states import AnnunciatorStates
from simulation.models.control_room_nmp2 import annunciators
from simulation.models.control_room_nmp2 import reactor_protection_system
import math

alarms_default = {
    "rps_a_auto_trip" : AnnunciatorStates.CLEAR,
    "rps_b_auto_trip" : AnnunciatorStates.CLEAR,
}

switches_default = {}

values_default = {}

indicators_default = {}

buttons_default = {
    "SCRAM_A1": False,
    "SCRAM_B1": False,
}

alarms = alarms_default
switches = switches_default
values = values_default
indicators = indicators_default
buttons = buttons_default

def model_run():
    #TODO: import reactor protection system and annunciator logic, and run them here
    annunciators.run(alarms)
    reactor_protection_system.run(alarms,buttons)