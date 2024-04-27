
from simulation.constants.annunciator_states import AnnunciatorStates
from server.server_events import server_rod_position_parameters_update_event
import math

rps_a_trip = False
rps_b_trip = False

def run(rods,alarms,buttons):
    #TODO: fire to client every rod's information (or, just ones that were updated)
    rod_position_information = {}
    accumulator_alarm = False
    drift_alarm = False

    for rod in rods:
        information = rods[rod]
        #if the rod is not driving, activate the drift alarm for that rod
        if information["insertion"] % 2 != 0 and not information["driving"]:
            information["drift_alarm"] = True

        if information["accum_trouble"] and not information["accum_trouble_acknowledged"]:
            accumulator_alarm = True

        if buttons["ROD_DRIFT_RESET"]:
            information["drift_alarm"] = False
        
        if buttons["ACCUM_TROUBLE_RESET"]:
            if information["accum_trouble"]:
                information["accum_trouble_acknowledged"] = True
            else:
                information["accum_trouble_acknowledged"] = False
                information["accum_trouble"] = False
        
        if information["drift_alarm"]:
            drift_alarm = True

        #if the accumulator pressure deviates too far , activate the accumulator alarm for that rod
        if information["accum_pressure"] > 1500 or information["accum_pressure"] < 600:
            information["accum_trouble"] = True

        rod_position_information[rod] = {}
        #this looks really messy, but it should hold true as we add more entries to every rod
        rod_position_information[rod]["scram"] = information["scram"]
        rod_position_information[rod]["insertion"] = information["insertion"]
        rod_position_information[rod]["accum_trouble"] = information["accum_trouble"]
        rod_position_information[rod]["accum_trouble_acknowledged"] = information["accum_trouble_acknowledged"]
        rod_position_information[rod]["select"] = information["select"]
        rod_position_information[rod]["drift_alarm"] = information["drift_alarm"]

    alarms["rod_drive_accumulator_trouble"]["alarm"] = accumulator_alarm
    alarms["control_rod_drift"]["alarm"] = drift_alarm

    server_rod_position_parameters_update_event.fire(rod_position_information) #TODO: update only the rods that NEED to be updated.