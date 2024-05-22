from simulation.constants.annunciator_states import AnnunciatorStates
import math

def run(alarms,buttons):

   for alarm in alarms:
      annunciator = alarms[alarm]
      group = annunciator["group"]
      #reflash + active normally
      if annunciator["alarm"] and (annunciator["state"] == AnnunciatorStates.CLEAR or annunciator["state"] == AnnunciatorStates.ACTIVE_CLEAR):
         annunciator["state"] = AnnunciatorStates.ACTIVE

      if not annunciator["alarm"] and annunciator["state"] == AnnunciatorStates.ACKNOWLEDGED:
         annunciator["state"] = AnnunciatorStates.ACTIVE_CLEAR
      
      #acknowledge behavior
      if annunciator["state"] == AnnunciatorStates.ACTIVE:
         for button in buttons:
            if "ALARM_ACK" in button and group in button and buttons[button]["state"]:
               annunciator["state"] = AnnunciatorStates.ACKNOWLEDGED
               annunciator["silenced"] = False

      #clear behavior
      if annunciator["state"] == AnnunciatorStates.ACTIVE_CLEAR:
         for button in buttons:
            if "ALARM_RESET" in button and group in button and buttons[button]["state"]:
               annunciator["state"] = AnnunciatorStates.CLEAR
               annunciator["silenced"] = False

      #silence behavior
      if annunciator["state"] == AnnunciatorStates.ACTIVE or annunciator["state"] == AnnunciatorStates.ACTIVE_CLEAR:
         for button in buttons:
            if "ALARM_SILENCE" in button and group in button and buttons[button]["state"]:
               annunciator["silenced"] = True

      #unsilence if the alarm comes back
               
      if annunciator["silenced"] and not annunciator["alarm"]:
         annunciator["silenced"] = False


      annunciator["alarm"] = False
