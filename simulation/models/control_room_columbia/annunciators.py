from simulation.constants.annunciator_states import AnnunciatorStates
from simulation.models.control_room_columbia import model
import math

def bisi(annunciator,name):
    if annunciator["alarm"]:
        assert name in model.buttons, "No pushbutton associated with "+name+" BISI!"
        if annunciator["state"] == AnnunciatorStates.CLEAR:
            annunciator["state"] = AnnunciatorStates.ACTIVE

        if model.buttons[name]["state"]:
            if annunciator["state"] == AnnunciatorStates.ACTIVE:
                annunciator["state"] = AnnunciatorStates.ACKNOWLEDGED
        
    else:
        annunciator["state"] = AnnunciatorStates.CLEAR

def run():

   for alarm in model.alarms:
      annunciator = model.alarms[alarm]
      group = annunciator["group"]

      if group == "-1": #this is a BISI
         bisi(annunciator,alarm)
         continue

      #reflash + active normally
      if annunciator["alarm"] and (annunciator["state"] == AnnunciatorStates.CLEAR or annunciator["state"] == AnnunciatorStates.ACTIVE_CLEAR):
         annunciator["state"] = AnnunciatorStates.ACTIVE

      if not annunciator["alarm"] and annunciator["state"] == AnnunciatorStates.ACKNOWLEDGED:
         annunciator["state"] = AnnunciatorStates.ACTIVE_CLEAR
      
      #acknowledge behavior
      if annunciator["state"] == AnnunciatorStates.ACTIVE:
         for button in model.buttons:
            if "ALARM_ACK" in button and group in button and model.buttons[button]["state"]:
               annunciator["state"] = AnnunciatorStates.ACKNOWLEDGED
               annunciator["silenced"] = False

      #clear behavior
      if annunciator["state"] == AnnunciatorStates.ACTIVE_CLEAR:
         for button in model.buttons:
            if "ALARM_RESET" in button and group in button and model.buttons[button]["state"]:
               annunciator["state"] = AnnunciatorStates.CLEAR
               annunciator["silenced"] = False

      #silence behavior
      if annunciator["state"] == AnnunciatorStates.ACTIVE or annunciator["state"] == AnnunciatorStates.ACTIVE_CLEAR:
         for button in model.buttons:
            if "ALARM_SILENCE" in button and group in button and model.buttons[button]["state"]:
               annunciator["silenced"] = True

      #at columbia, pressing any main panel acknowledge will silence all alarms for other main panels.
      #this was done because there was not enough room for silence pushbuttons (and they already laid out the panels)
      for button in model.buttons:
         #TODO: blacklist/whitelist groups together
         if "ALARM_ACK" in button and model.buttons[button]["state"]:
            annunciator["silenced"] = True

      #unsilence if the alarm comes back
               
      if annunciator["silenced"] and not annunciator["alarm"]:
         annunciator["silenced"] = False


      annunciator["alarm"] = False
