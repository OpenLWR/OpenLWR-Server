from simulation.constants.annunciator_states import AnnunciatorStates
import math

def run(alarms):
   #TODO: how should we detect when to trigger these annunciators?
   for alarm in alarms:
      alarms[alarm] = AnnunciatorStates.CLEAR
