from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia import rod_position_information_system
from simulation.models.control_room_columbia import reactor_protection_system

latched_group = 1

rwm = {
    "initialized" : False,
    "inop" : False,
    "manual_bypass" : False,
    "group" : 1,
    "withdraw_blocks" : [],
    "insert_blocks" : [],
    "withdraw_errors" : {},
    "insert_errors" : {},
    "select_error" : False,
    "program_alarm" : False,
    "computer_alarm" : False,
    "diag_pressed" : False,
    "diagnostic_mode" : False,
    "test_pressed" : False,
    "rod_test_mode" : False,
}

def blank_rwm():
    model.values["rwm_group"] = -1 #-1 is blank
    model.values["rwm_insert_error_1"] = -1
    model.values["rwm_insert_error_2"] = -1
    model.values["rwm_withdraw_error"] = -1

def blank_alarms():
    model.indicators["rwm_select_error"] = False
    model.indicators["rwm_lpap"] = False
    model.indicators["rwm_lpsp"] = False
    model.indicators["rwm_seq"] = False

def rwm_buttons():
    if model.buttons["rwm_seq"]["state"]:
        rwm["initialized"] = True

        #TODO: this should initialize a latching operation

    model.indicators["rwm_init"] = model.buttons["rwm_seq"]["state"]

    if model.buttons["rwm_test"]["state"] and not rwm["test_pressed"]:
        all_rods_in = True
        for rod in model.rods:
            rod = model.rods[rod]
            if rod["insertion"] > 0:
                all_rods_in = False

        if all_rods_in and not rwm["rod_test_mode"]:
            rwm["rod_test_mode"] = True
        elif rwm["rod_test_mode"]:
            rwm["rod_test_mode"] = False

    model.indicators["rwm_select"] = rwm["rod_test_mode"]
    rwm["test_pressed"] = model.buttons["rwm_test"]["state"]

    if model.buttons["rwm_diag"]["state"] and not rwm["diag_pressed"]:
        #i dont have very good info on the diagnostic mode
        if rwm["diagnostic_mode"]:
            rwm["initialized"] = False #RWM must be initialized again after a diagnostic
        rwm["diagnostic_mode"] = not rwm["diagnostic_mode"]

    rwm["diag_pressed"] = model.buttons["rwm_diag"]["state"]
    
    if model.buttons["rwm_rwm_comp_prog"]["state"]:
        #all indicators light when this is pressed
        model.indicators["rwm_rwm"] = True
        model.indicators["rwm_comp"] = True
        model.indicators["rwm_prog"] = True
        rwm["computer_alarm"] = False
        rwm["program_alarm"] = False

def run():
    if rwm["initialized"] :
        model.values["rwm_group"] = rwm["group"]
    else:
        blank_rwm()
    
    #prog illuminates if not init, manually bypassed, or program aborted
    if (not rwm["initialized"]) or rwm["manual_bypass"]:
        rwm["program_alarm"] = True #this is seal-in

    model.indicators["rwm_prog"] = rwm["program_alarm"]

    model.indicators["rwm_comp"] = rwm["computer_alarm"]

    #R304B says "RWM" lights up whenever COMP or PROG is in alarm

    model.indicators["rwm_rwm"] = model.indicators["rwm_comp"] or model.indicators["rwm_prog"] 

    rwm_buttons()

    if rwm["diagnostic_mode"]:
        #TODO: make it remove/insert periodically
        if "diagnostic" not in rwm["withdraw_blocks"]:
            rwm["withdraw_blocks"].append("diagnostic")
        
        if "diagnostic" not in rwm["insert_blocks"]:
            rwm["insert_blocks"].append("diagnostic")

    else:
        if "diagnostic" in rwm["withdraw_blocks"]:
            rwm["withdraw_blocks"].remove("diagnostic")

        if "diagnostic" in rwm["insert_blocks"]:
            rwm["insert_blocks"].remove("diagnostic")


    if rwm["rod_test_mode"]:
        rods_out = 0
        for rod in model.rods:
            rod = model.rods[rod]
            if rod["insertion"] > 0:
                rods_out += 1

        if rods_out > 1 and not "Rod Test More Than 1 Out" in rwm["withdraw_blocks"]:
            rwm["withdraw_blocks"].append("Rod Test More Than 1 Out")
        elif rods_out <= 1 and "Rod Test More Than 1 Out" in rwm["withdraw_blocks"]:
            rwm["withdraw_blocks"].remove("Rod Test More Than 1 Out")
    else:
        if "Rod Test More Than 1 Out" in rwm["withdraw_blocks"]:
            rwm["withdraw_blocks"].remove("Rod Test More Than 1 Out")

    blank = rwm["manual_bypass"]
    #TODO: unindent all of this
    if rwm["initialized"]: 
        model.indicators["rwm_manual"] = rwm["manual_bypass"]
        # TODO: automatic bypass
        
        if blank:
            blank_rwm()
            blank_alarms()
            
            rwm["withdraw_blocks"] = []
            rwm["insert_blocks"] = []
            model.indicators["rwm_insert_block"] = False
            model.indicators["rwm_withdraw_block"] = False
            
    
        if not rwm["inop"] and not blank and not rwm["rod_test_mode"]:
            calculate_data()
            
            # TODO: RWM LPAP/LPSP steam flow bypasses
            lpap_reached = False
            model.indicators["rwm_lpap"] = True
            model.indicators["rwm_lpsp"] = True
            
            #this light only comes in when in the transition zone (LPAP) 
            model.indicators["rwm_seq"] = (len(rwm["insert_errors"]) > 2 or rwm["withdraw_errors"] != {}) and lpap_reached
            
            model.values["rwm_withdraw_error"] = -1
            for rod in rwm["withdraw_errors"]:
                rod_1 = rod.split("-")[0]
                rod_2 = rod.split("-")[1]
                rod = rod_1+rod_2
                rod = 10000+int(rod)
                model.values["rwm_withdraw_error"] = rod
            
            
            model.values["rwm_insert_error_1"] = -1
            model.values["rwm_insert_error_2"] = -1
            runs = 0
            for rod in rwm["insert_errors"]:
                rod_1 = rod.split("-")[0]
                rod_2 = rod.split("-")[1]
                rod = rod_1+rod_2
                rod = 10000+int(rod)

                if runs == 0:
                    model.values["rwm_insert_error_2"] = rod
                if runs == 1:
                    model.values["rwm_insert_error_1"] = rod
                    break
                runs += 1
                
            rwm["select_error"] = True
            group_info = groups["sequence_a"][rwm["group"]]
            for rod_number in group_rods["sequence_a"][group_info["rod_group"]]:
                
                if "|" in rod_number:
                    rod_number = rod_number.split("|")[0]
                
                #TODO: select errors during insert/withdraw blocks
                if rod_position_information_system.selected_rod == rod_number:
                    rwm["select_error"] = False
                    break
            
            model.indicators["rwm_select_error"] = rwm["select_error"]
            
        elif not blank and not rwm["rod_test_mode"]:
            if not "rwm_inop" in rwm["withdraw_blocks"]:
                rwm["withdraw_blocks"].append("rwm_inop")
            if not "rwm_inop" in rwm["insert_blocks"]:
                rwm["insert_blocks"].append("rwm_inop")
        
        if rwm["withdraw_blocks"] != []:
            model.indicators["rwm_withdraw_block"] = True
            reactor_protection_system.add_withdraw_block("RWM")
        else:
            model.indicators["rwm_withdraw_block"] = False
            reactor_protection_system.remove_withdraw_block("RWM")
        if rwm["insert_blocks"] != []:
            model.indicators["rwm_insert_block"] = True
            reactor_protection_system.add_insert_block("RWM")
        else:
            model.indicators["rwm_insert_block"] = False
            reactor_protection_system.remove_insert_block("RWM")

def calculate_data():
    # calculate the group
    global latched_group
    latched_group = 1
    for group_number in groups["sequence_a"]:
        
        # check that all groups 1 through latched_group-1 have <3 insert errors
        insert_error_count = 0
        
        for group_number_2 in groups["sequence_a"]:
            if group_number_2 >= latched_group: break
            
            group_info = groups["sequence_a"][group_number_2]
            withdraw_limit = group_info["max_position"]
            alternate_withdraw_limit = withdraw_limit - 2
            
            for rod_number in group_rods["sequence_a"][group_info["rod_group"]]:
                if "|" in rod_number:
                    rod_number = rod_number.split("|")[0]
                if int(model.rods[rod_number]["insertion"]) < withdraw_limit and int(model.rods[rod_number]["insertion"]) < alternate_withdraw_limit:
                    insert_error_count += 1
        
        one_rod_past_insert_limit = False
        group_info = groups["sequence_a"][group_number]
        insert_limit = group_info["min_position"]
        
        for rod_number in group_rods["sequence_a"][group_info["rod_group"]]:
            if "|" in rod_number:
                rod_number = rod_number.split("|")[0]
            if int(model.rods[rod_number]["insertion"]) > insert_limit:
                one_rod_past_insert_limit = True
                break
        
        if insert_error_count > 3 or not one_rod_past_insert_limit:
            if latched_group != 1:
                latched_group -= 1
            break
        elif latched_group < 72:
            latched_group += 1
            
    rwm["group"] = latched_group
    
    # calculate errors
    insert_errors = {}
    withdraw_errors = {}
    for group_number in groups["sequence_a"]:
        
        group_info = groups["sequence_a"][group_number]
        withdraw_limit = group_info["max_position"]
        alternate_withdraw_limit = withdraw_limit - 2
        insert_limit = group_info["min_position"]
        alternate_insert_limit = insert_limit - 2 if insert_limit != 0 else 2
        
        for rod_number in group_rods["sequence_a"][group_info["rod_group"]]:
            if "|" in rod_number:
                rod_number = rod_number.split("|")[0]
                
            
            insert_error = False    
            withdraw_error = False
            
            rod = model.rods[rod_number]["insertion"]

            if group_number == rwm["group"]:
                insert_error = int(rod) < insert_limit and int(rod) < alternate_insert_limit
                withdraw_error = int(rod) > withdraw_limit
            elif group_number < rwm["group"]:
                insert_error = int(rod) < withdraw_limit and int(rod) < alternate_withdraw_limit
                withdraw_error = int(rod) > withdraw_limit
            elif group_number > rwm["group"]:
                insert_error = False
                withdraw_error = int(rod) > insert_limit
            
            if rod_number in withdraw_errors and not withdraw_error:
                del withdraw_errors[rod_number]
                
            if insert_error and rod_number not in insert_errors:
                insert_errors[rod_number] = {
                    # these extra information are unused for now, but i'm leaving them here just in case
                    "group_number": group_number,
                    "rod_group": group_info["rod_group"]
                }
                
            if withdraw_error and rod_number not in withdraw_errors:
                withdraw_errors[rod_number] = {
                    "group_number": group_number,
                    "rod_group": group_info["rod_group"]
                }
                
    if withdraw_errors != {} and not "Withdraw Error" in rwm["withdraw_blocks"]:
        rwm["withdraw_blocks"].append("Withdraw Error")
    elif "Withdraw Error" in rwm["withdraw_blocks"] and withdraw_errors == {}:
        rwm["withdraw_blocks"].remove("Withdraw Error")
                    
    if len(insert_errors) > 2 and not "Insert Error" in rwm["insert_blocks"]:
        rwm["insert_blocks"].append("Insert Error")
    elif "Insert Error" in rwm["insert_blocks"] and len(insert_errors) < 3:
        rwm["insert_blocks"].remove("Insert Error")
                
    if (len(insert_errors) >= 3 and rod_position_information_system.selected_rod not in insert_errors) and ("Insert error with selection error" not in rwm["withdraw_blocks"]):
        rwm["withdraw_blocks"].append("Insert error with selection error")
    elif "Insert error with selection error" in rwm["withdraw_blocks"] and not (len(insert_errors) >= 3 and rod_position_information_system.selected_rod not in insert_errors):
        rwm["withdraw_blocks"].remove("Insert error with selection error")

    rwm["withdraw_errors"] = withdraw_errors
    rwm["insert_errors"] = insert_errors

def withdraw_next():
    last_rod = True
    parameters_for_group = groups["sequence_a"][latched_group]
    for rod in group_rods["sequence_a"][parameters_for_group["rod_group"]]:
        max_this_group = parameters_for_group["max_position"]
        if model.rods[rod]["insertion"] != max_this_group:
            model.rods[rod]["insertion"] = max_this_group
            last_rod = False
            break

    #now we know all rods in this group are out, withdraw the first in the next
    if last_rod:
        parameters_for_group = groups["sequence_a"][latched_group+1]
        max_this_group = parameters_for_group["max_position"]
        model.rods[group_rods["sequence_a"][parameters_for_group["rod_group"]][0]]["insertion"] = max_this_group

# rod group data begins here
# TODO: add sequence B (found in NRC document ML20136H955)
groups = {
    "sequence_a": {
        1: {
            "rod_group":1,
            "min_position":0,
            "max_position":48,
        },
        2: {
            "rod_group":2,
            "min_position":0,
            "max_position":48,
        },
        3: {
            "rod_group":3,
            "min_position":0,
            "max_position":48,
        },
        4: {
            "rod_group":4,
            "min_position":0,
            "max_position":48,
        },
        5: {
            "rod_group":5,
            "min_position":0,
            "max_position":48,
        },
        6: {
            "rod_group":6,
            "min_position":0,
            "max_position":48,
        },
        7: {
            "rod_group":7,
            "min_position":0,
            "max_position":48,
        },
        8: {
            "rod_group":8,
            "min_position":0,
            "max_position":48,
        },
        9: {
            "rod_group":9,
            "min_position":0,
            "max_position":48,
        },
        10: {
            "rod_group":10,
            "min_position":0,
            "max_position":48,
        },
        11: {
            "rod_group":11,
            "min_position":0,
            "max_position":48,
        },
        12: {
            "rod_group":12,
            "min_position":0,
            "max_position":4,
        },
        13: {
            "rod_group":12,
            "min_position":4,
            "max_position":8,
        },
        14: {
            "rod_group":13,
            "min_position":0,
            "max_position":4,
        },
        15: {
            "rod_group":12,
            "min_position":8,
            "max_position":12,
        },
        16: {
            "rod_group":13,
            "min_position":4,
            "max_position":8,
        },
        17: {
            "rod_group":14,
            "min_position":0,
            "max_position":4,
        },
        18: {
            "rod_group":15,
            "min_position":0,
            "max_position":4,
        },
        19: {
            "rod_group":12,
            "min_position":12,
            "max_position":16,
        },
        20: {
            "rod_group":13,
            "min_position":8,
            "max_position":12,
        },
        21: {
            "rod_group":12,
            "min_position":16,
            "max_position":20,
        },
        22: {
            "rod_group":13,
            "min_position":12,
            "max_position":16,
        },
        23: {
            "rod_group":14,
            "min_position":4,
            "max_position":8,
        },
        24: {
            "rod_group":15,
            "min_position":4,
            "max_position":8,
        },
        25: {
            "rod_group":12,
            "min_position":20,
            "max_position":24,
        },
        26: {
            "rod_group":13,
            "min_position":16,
            "max_position":20,
        },
        27: {
            "rod_group":14,
            "min_position":8,
            "max_position":12,
        },
        28: {
            "rod_group":12,
            "min_position":24,
            "max_position":30,
        },
        29: {
            "rod_group":13,
            "min_position":20,
            "max_position":24,
        },
        30: {
            "rod_group":14,
            "min_position":12,
            "max_position":16,
        },
        31: {
            "rod_group":12,
            "min_position":30,
            "max_position":36,
        },
        32: {
            "rod_group":13,
            "min_position":24,
            "max_position":30,
        },
        33: {
            "rod_group":14,
            "min_position":12,
            "max_position":16,
        },
        34: {
            "rod_group":15,
            "min_position":8,
            "max_position":14,
        },
        35: {
            "rod_group":12,
            "min_position":36,
            "max_position":42,
        },
        36: {
            "rod_group":13,
            "min_position":30,
            "max_position":36,
        },
        37: {
            "rod_group":16,
            "min_position":0,
            "max_position":4,
        },
        38: {
            "rod_group":14,
            "min_position":20,
            "max_position":24,
        },
        39: {
            "rod_group":15,
            "min_position":14,
            "max_position":18,
        },
        40: {
            "rod_group":12,
            "min_position":42,
            "max_position":48,
        },
        41: {
            "rod_group":13,
            "min_position":36,
            "max_position":42,
        },
        42: {
            "rod_group":16,
            "min_position":4,
            "max_position":8,
        },
        43: {
            "rod_group":17,
            "min_position":0,
            "max_position":4,
        },
        44: {
            "rod_group":18,
            "min_position":0,
            "max_position":4,
        },
        45: {
            "rod_group":14,
            "min_position":24,
            "max_position":28,
        },
        46: {
            "rod_group":15,
            "min_position":18,
            "max_position":22,
        },
        47: {
            "rod_group":13,
            "min_position":42,
            "max_position":48,
        },
        48: {
            "rod_group":17,
            "min_position":4,
            "max_position":8,
        },
        49: {
            "rod_group":14,
            "min_position":28,
            "max_position":32,
        },
        50: {
            "rod_group":15,
            "min_position":22,
            "max_position":26,
        },
        51: {
            "rod_group":19,
            "min_position":0,
            "max_position":4,
        },
        52: {
            "rod_group":14,
            "min_position":32,
            "max_position":36,
        },
        53: {
            "rod_group":15,
            "min_position":26,
            "max_position":30,
        },
        54: {
            "rod_group":16,
            "min_position":8,
            "max_position":12,
        },
        55: {
            "rod_group":17,
            "min_position":8,
            "max_position":12,
        },
        56: {
            "rod_group":18,
            "min_position":4,
            "max_position":8,
        },
        57: {
            "rod_group":20,
            "min_position":0,
            "max_position":4,
        },
        58: {
            "rod_group":16,
            "min_position":12,
            "max_position":16,
        },
        59: {
            "rod_group":19,
            "min_position":4,
            "max_position":8,
        },
        60: {
            "rod_group":20,
            "min_position":4,
            "max_position":8,
        },
        61: {
            "rod_group":18,
            "min_position":8,
            "max_position":12,
        },
        62: {
            "rod_group":17,
            "min_position":12,
            "max_position":16,
        },
        63: {
            "rod_group":19,
            "min_position":8,
            "max_position":12,
        },
        64: {
            "rod_group":21,
            "min_position":8,
            "max_position":12,
        },
        65: {
            "rod_group":16,
            "min_position":16,
            "max_position":20,
        },
        66: {
            "rod_group":22,
            "min_position":36,
            "max_position":42,
        },
        67: {
            "rod_group":23,
            "min_position":36,
            "max_position":42,
        },
        68: {
            "rod_group":24,
            "min_position":30,
            "max_position":36,
        },
        69: {
            "rod_group":20,
            "min_position":8,
            "max_position":12,
        },
        70: {
            "rod_group":17,
            "min_position":16,
            "max_position":20,
        },
        71: {
            "rod_group":25,
            "min_position":12,
            "max_position":16,
        },
        72: {
            "rod_group":21,
            "min_position":12,
            "max_position":16,
        },
    }
}

group_rods = {
    "sequence_a": {
        1: [
            "26-31",
            "34-39",
            "42-31",
            "34-23",
            "26-15",
            "18-23",
            "10-31",
            "18-39",
            "26-47",
            "42-47",
            "50-39",
            "50-23",
            "42-15",
            "34-07",
            "18-07",
            "10-15",
            "02-23",
            "02-39",
            "10-47",
            "18-55",
            "34-55",
            "58-31",
        ],
        2: [
            "34-31",
            "26-23",
            "18-31",
            "26-39",
            "34-47",
            "42-39",
            "50-31",
            "42-23",
            "34-15",
            "18-15",
            "10-23",
            "10-39",
            "18-47",
            "26-55",
            "42-55",
            "50-47",
            "58-39",
            "58-23",
            "50-15",
            "42-07",
            "26-07",
            "02-31",
        ],
        3: [
            "30-35",
            "38-27",
            "30-19",
            "22-27",
            "14-35",
            "22-43",
            "30-51",
            "38-43",
            "46-35",
            "54-27",
            "46-19",
            "38-11",
            "22-11",
            "14-19",
            "06-27",
            "06-43",
            "14-51",
            "22-59",
            "38-59",
            "46-51",
            "54-43",
            "30-03",
        ],
        4: [
            "30-27",
            "22-35",
            "30-43",
            "38-35",
            "46-27",
            "38-19",
            "30-11",
            "22-19",
            "14-27",
            "14-43",
            "22-51",
            "38-51",
            "46-43",
            "54-35",
            "54-19",
            "46-11",
            "38-03",
            "22-03",
            "14-11",
            "06-19",
            "06-35",
            "30-59",
        ],
        5: [
            "58-43",
            "42-03",
            "02-19",
            "18-59",
            "58-19",
            "18-03",
            "02-43",
            "42-59",
        ],
        6: [
            "50-11",
            "10-11",
            "10-51",
            "50-51",
        ], 
        7: [
            "42-19",
            "18-19",
            "18-43",
            "42-43",
        ],
        8: [
            "34-27",
            "26-27",
            "26-35",
            "34-35",
        ],
        9: [
            "34-03",
            "02-27",
            "26-59",
            "58-35",
            "26-03",
            "02-35",
            "34-59",
            "58-27",
        ],
        10: [
            "14-07",
            "06-47",
            "46-55",
            "54-15",
            "06-15",
            "14-55",
            "54-47",
            "46-07",
        ],
        11: [
            "18-27",
            "26-43",
            "42-35",
            "34-19",
            "18-35",
            "34-43",
            "42-27",
            "26-19",
        ],
        12: [
            "18-11",
            "10-43",
            "42-51",
            "50-19",
            "42-11",
            "10-19",
            "18-51",
            "50-43",
        ],
        13: [
            "26-11",
            "10-35",
            "34-51",
            "50-27",
            "34-11",
            "10-27",
            "26-51",
            "50-35",
        ],
        14: [
            "22-47|22",
            "46-39|22",
            "38-15|22",
            "14-23|22",
            "22-15|23",
            "14-39|23",
            "38-47|23",
            "46-23|23",
        ],
        15: [
            "30-23|24",
            "22-31|24",
            "30-39|24",
            "38-31|24",
        ],
        16: [
            "30-07",
            "06-31",
            "30-55",
            "54-31",
        ],
        17: [
            "14-15",
            "14-47",
            "46-47",
            "46-15",
        ],
        18: [
            "30-31",
            "22-39",
            "38-39",
            "38-23",
            "22-23",
        ],
        19: [
            "22-07|25",
            "06-39|25",
            "38-55|25",
            "54-23|25",
            "38-07|21",
            "06-23|21",
            "22-55|21",
            "54-39|21",
        ],
        20: [
            "14-31",
            "30-15",
            "46-31",
            "30-47",
        ],
        21: [
            "38-07",
            "06-23",
            "22-55",
            "54-39",
        ],
        22: [
            "22-47",
            "46-39",
            "38-15",
            "14-23",
        ],
        23: [
            "22-15",
            "14-39",
            "38-47",
            "46-23",
        ],
        24: [
            "30-23",
            "22-31",
            "30-39",
            "38-31",
        ],
        25: [
            "22-07",
            "06-39",
            "38-55",
            "54-23",
        ],
    },
}
