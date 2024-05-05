
from simulation.constants.annunciator_states import AnnunciatorStates
from server.server_events import server_rod_position_parameters_update_event
import math

def run(rods,alarms,buttons):
    #TODO: fire to client every rod's information (or, just ones that were updated)
    rod_position_information = {}
    accumulator_alarm = False
    drift_alarm = False
    selected_rod = "none"

    for rod in rods:
        information = rods[rod]
        #if the rod is not driving, activate the drift alarm for that rod

        if information["select"]:
            selected_rod = rod

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

    four_rod_display(selected_rod)

    server_rod_position_parameters_update_event.fire(rod_position_information) #TODO: update only the rods that NEED to be updated.

select_groups = {
	1: {
		1: "06-23",
		2: "02-23",
		3: "06-19",
		4: "02-19",
	},
	2: {
		1: "14-23",
		2: "10-23",
		3: "14-19",
		4: "10-19",
	},
	3: {
		1: "22-23",
		2: "18-23",
		3: "22-19",
		4: "18-19",
	},
	4: {
		1: "30-23",
		2: "26-23",
		3: "30-19",
		4: "26-19",
	},
	5: {
		1: "38-23",
		2: "34-23",
		3: "38-19",
		4: "34-19",
	},
	6: {
		1: "46-23",
		2: "42-23",
		3: "46-19",
		4: "42-19",
	},
	7: {
		1: "54-23",
		2: "50-23",
		3: "54-19",
		4: "50-19",
	},
	8: {
		1: "none",
		2: "58-23",
		3: "none",
		4: "58-19",
	},
	9: {
		1: "06-31",
		2: "02-31",
		3: "06-27",
		4: "02-27",
	},
	10: {
		1: "14-31",
		2: "10-31",
		3: "14-27",
		4: "10-27",
	},
	11: {
		1: "22-31",
		2: "18-31",
		3: "22-27",
		4: "18-27",
	},
	12: {
		1: "30-31",
		2: "26-31",
		3: "30-27",
		4: "26-27",
	},
	13: {
		1: "38-31",
		2: "34-31",
		3: "38-27",
		4: "34-27",
	},
	14: {
		1: "46-31",
		2: "42-31",
		3: "46-27",
		4: "42-27",
	},
	15: {
		1: "54-31",
		2: "50-31",
		3: "54-27",
		4: "50-27",
	},
	16: {
		1: "none",
		2: "58-31",
		3: "none",
		4: "58-27",
	},
	17: {
		1: "06-39",
		2: "02-39",
		3: "06-35",
		4: "02-35",
	},
	18: {
		1: "14-39",
		2: "10-39",
		3: "14-35",
		4: "10-35",
	},
	19: {
		1: "22-39",
		2: "18-39",
		3: "22-35",
		4: "18-35",
	},
	20: {
		1: "30-39",
		2: "26-39",
		3: "30-35",
		4: "26-35",
	},
	21: {
		1: "38-39",
		2: "34-39",
		3: "38-35",
		4: "34-35",
	},
	22: {
		1: "46-39",
		2: "42-39",
		3: "46-35",
		4: "42-35",
	},
	23: {
		1: "54-39",
		2: "50-39",
		3: "54-35",
		4: "50-35",
	},
	24: {
		1: "none",
		2: "58-39",
		3: "none",
		4: "58-35",
	},
	25: {
		1: "06-47",
		2: "none",
		3: "06-43",
		4: "02-43",
	},
	26: {
		1: "14-47",
		2: "10-47",
		3: "14-43",
		4: "10-43",
	},
	27: {
		1: "22-47",
		2: "18-47",
		3: "22-43",
		4: "18-43",
	},
	28: {
		1: "30-47",
		2: "26-47",
		3: "30-43",
		4: "26-43",
	},
	29: {
		1: "38-47",
		2: "34-47",
		3: "38-43",
		4: "34-43",
	},
	30: {
		1: "46-47",
		2: "42-47",
		3: "46-43",
		4: "42-43",
	},
	31: {
		1: "54-47",
		2: "50-47",
		3: "54-43",
		4: "50-43",
	},
	32: {
		1: "none",
		2: "none",
		3: "none",
		4: "58-43",
	},
	33: {
		1: "14-55",
		2: "none",
		3: "14-51",
		4: "10-51",
	},
	34: {
		1: "22-55",
		2: "18-55",
		3: "22-51",
		4: "18-51",
	},
	35: {
		1: "30-55",
		2: "26-55",
		3: "30-51",
		4: "26-51",
	},
	36: {
		1: "38-55",
		2: "34-55",
		3: "38-51",
		4: "34-51",
	},
	37: {
		1: "46-55",
		2: "42-55",
		3: "46-51",
		4: "42-51",
	},
	38: {
		1: "none",
		2: "none",
		3: "none",
		4: "50-51",
	},
	39: {
		1: "none",
		2: "none",
		3: "22-59",
		4: "18-59",
	},
	40: {
		1: "none",
		2: "none",
		3: "30-59",
		4: "26-59",
	},
	41: {
		1: "none",
		2: "none",
		3: "38-59",
		4: "34-59",
	},
	42: {
		1: "none",
		2: "none",
		3: "none",
		4: "42-59",
	},
	43: {
		1: "14-07",
		2: "none",
		3: "none",
		4: "none",
	},
	44: {
		1: "22-07",
		2: "18-07",
		3: "22-03",
		4: "18-03",
	},
	45: {
		1: "30-07",
		2: "26-07",
		3: "30-03",
		4: "26-03",
	},
	46: {
		1: "38-07",
		2: "34-07",
		3: "38-03",
		4: "34-03",
	},
	47: {
		1: "46-07",
		2: "42-07",
		3: "none",
		4: "42-03",
	},
	48: {
		1: "14-15",
		2: "10-15",
		3: "14-11",
		4: "10-11",
	},
	49: {
		1: "22-15",
		2: "18-15",
		3: "22-11",
		4: "18-11",
	},
	50: {
		1: "30-15",
		2: "26-15",
		3: "30-11",
		4: "26-11",
	},
	51: {
		1: "38-15",
		2: "34-15",
		3: "38-11",
		4: "34-11",
	},
	52: {
		1: "46-15",
		2: "42-15",
		3: "46-11",
		4: "42-11",
	},
	53: {
		1: "06-15",
		2: "none",
		3: "none",
		4: "none",
	},
	54: {
		1: "54-15",
		2: "50-15",
		3: "none",
		4: "50-11",
	},
}

selected_group = 1

def four_rod_display(selected_rod):
    from simulation.models.control_room_nmp2 import model
    global selected_group
    global select_groups

    if not selected_rod in select_groups[selected_group]:
        for group in select_groups:
            grp = select_groups[group]
            for rod in grp:
                rod = grp[rod]
                if rod == selected_rod:
                    selected_group = group
                    break

    for rod_num in select_groups[selected_group]:

        rod = select_groups[selected_group][rod_num]
        if rod != "none":
            value = round(model.rods[rod]["insertion"])
            failed = model.rods[rod]["reed_switch_fail"]
        else:
            value = "none"
        select = rod == selected_rod
        undisplayable = value < 0 or value > 48 or (value % 2 != 0)
        
        blank = value == "none"

        value+=1 #we add one so the client doesnt receive a "0" as a position

        if undisplayable: #displays "- -"
            value = 60
        elif failed: #displays "X X"
            value = 70
        elif blank: #blank
            value = 80

        if select: value = value*-1

        match rod_num:
            case 1: model.values["four_rod_tr"] = value
            case 2: model.values["four_rod_tl"] = value
            case 3: model.values["four_rod_br"] = value
            case 4: model.values["four_rod_bl"] = value




