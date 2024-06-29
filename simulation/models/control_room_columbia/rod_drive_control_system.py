import math
from simulation.models.control_room_columbia import reactor_protection_system
from simulation.models.control_room_columbia import model
from threading import Thread
any_rod_driving = False
select_block = False
withdraw_pressed = False

def run(rods,buttons):
    any_rod_driving = False
    global select_block
    global withdraw_pressed

    refuel_mode = (model.switches["reactor_mode_switch"]["position"] == model.ReactorMode.REFUEL) 
    select_block = False

    if refuel_mode:
        all_rods_in = True
        for r in model.rods:
            r = model.rods[r]
            if r["insertion"] > 0:
                all_rods_in = False

        if not all_rods_in:
            select_block = True

    model.indicators["RMCS_SELECT_BLOCK"] = select_block

    for rod in rods:
        info = rods[rod]

        if info["driving"] : any_rod_driving = True

        if info["select"] and not any_rod_driving:
            if buttons["RMCS_INSERT_PB"]["state"]:
                insert_rod(rod)
            elif buttons["RMCS_WITHDRAW_PB"]["state"] and not withdraw_pressed:
                withdraw_rod(rod)
            elif buttons["RMCS_CONT_WITHDRAW_PB"]["state"]:
                cont_withdraw_rod(rod)
            elif buttons["RMCS_CONT_INSERT_PB"]["state"]:
                cont_insert_rod(rod)

        #TODO: Move to CRD system?
        #rod drifting OUT when not latched
        if (not info["driving"]) and (info["insertion"] % 2) != 0 and not info["scram"]:
            if info["driftto"] == -15:
                info["driftto"] = math.floor(max(min(info["insertion"]+1,50),0))
            
            info["insertion"] += 9*0.001
            if info["insertion"] > info["driftto"]:
                info["insertion"] = info["driftto"]
                info["driftto"] = -15

            if info["insertion"]> 48:
                info["insertion"] = 48
        
        else:
            info["driftto"] = -15


        if info["scram"]:
            #TODO: accumulator pressure and its affect on rod drive
            if info["insertion"] > 0:
                info["insertion"] = info["insertion"] - 1.6 #approximately 3 seconds to scram from full out
                info["accum_pressure"] = info["accum_pressure"] - 30 #approximately 2 seconds until the accumulator alarm activates
            else:
                info["insertion"] = 0


    withdraw_pressed = buttons["RMCS_WITHDRAW_PB"]["state"]

def insert_rod(rod:str):

    #check if this rod movement is valid first before starting the thread
    if reactor_protection_system.insert_block: 
        return

    from simulation.models.control_room_columbia import model

    current_rod = model.rods[rod]
    current_insertion = current_rod["insertion"]

    if int(current_insertion) <= 0:
        return
    
    motion = Thread(target=insert_rod_motion,args=(rod,))
    motion.start()

def insert_rod_motion(args):
    import time
    from simulation.models.control_room_columbia import model
    rod = args
    #time delay to insert control
    time.sleep(0.04)
    current_rod = model.rods[rod]
    current_insertion = current_rod["insertion"]
    model.rods[rod]["driving"] = True

    insertion = current_insertion
    target_insertion = insertion-2

    model.indicators["RMCS_INSERT"] = True

    #holding down "insert" inserts the rod for however long its pressed, but still end with a settle sequence.
    #This is different from continuous insert, as that does not have a settle sequence.
    
    #insert the rod for 2.9 seconds
    runs = 0
    while runs < 29:
        model.rods[rod]["insertion"] = model.rods[rod]["insertion"] - 0.082
        time.sleep(0.11)
        if model.buttons["RMCS_INSERT_PB"]["state"] and runs >= 28 and not reactor_protection_system.insert_block:
            runs = 0
            model.rods[rod]["insertion"] = target_insertion
            target_insertion = model.rods[rod]["insertion"] - 2
        else:
            runs += 1

    model.indicators["RMCS_INSERT"] = False

    model.indicators["RMCS_SETTLE"] = True

    #start the settle motion

    runs = 0
    while runs < 53:
        if insertion >= target_insertion:
            insertion = target_insertion
        else:
            insertion += 0.0076

        model.rods[rod]["insertion"] = insertion
        time.sleep(0.11)
        runs += 1

    if not model.rods[rod]["scram"]:
        model.rods[rod]["insertion"] = target_insertion

    model.rods[rod]["driving"] = False
    model.indicators["RMCS_SETTLE"] = False

#Continuous Insert (probably spelled wrong)
#Cont insert has NO settle sequence
#When the pushbutton is released, the insert valve instantly closes and the rod drifts to a position through the CRD seals
#This allows quickly inserting rods in an emergency
def cont_insert_rod(rod:str):

    #check if this rod movement is valid first before starting the thread
    if reactor_protection_system.insert_block: 
        return

    from simulation.models.control_room_columbia import model

    current_rod = model.rods[rod]
    current_insertion = current_rod["insertion"]

    if int(current_insertion) <= 0:
        return
    
    motion = Thread(target=cont_insert_rod_motion,args=(rod,))
    motion.start()



def cont_insert_rod_motion(args):
    import time
    from simulation.models.control_room_columbia import model
    rod = args
    #time delay to insert control
    time.sleep(0.04)
    model.rods[rod]["driving"] = True

    model.indicators["RMCS_INSERT"] = True
    
    #insert the rod as long as insert is depressed
    while model.buttons["RMCS_CONT_INSERT_PB"]["state"] and not reactor_protection_system.insert_block:
        model.rods[rod]["insertion"] = model.rods[rod]["insertion"] - 0.082
        time.sleep(0.11)

    model.indicators["RMCS_INSERT"] = False

    model.rods[rod]["driving"] = False


def withdraw_rod(rod:str):

    #check if this rod movement is valid first before starting the thread
    if reactor_protection_system.withdraw_block: 
        return

    from simulation.models.control_room_columbia import model

    current_rod = model.rods[rod]
    current_insertion = current_rod["insertion"]

    #TODO: overtravel test
    if int(current_insertion) >= 48:
        return
    
    motion = Thread(target=withdraw_rod_motion,args=(rod,))
    motion.start()

def withdraw_rod_motion(args):
    import time
    from simulation.models.control_room_columbia import model
    rod = args
    #time delay to insert control
    time.sleep(0.04)
    current_rod = model.rods[rod]
    current_insertion = current_rod["insertion"]
    model.rods[rod]["driving"] = True

    insertion = current_insertion
    target_insertion = insertion+2

    model.indicators["RMCS_INSERT"] = True

    #insert (unlatch) for 0.6 seconds
    runs = 0
    while runs < 6 and not model.rods[rod]["scram"]:
        insertion -= 0.082
        model.rods[rod]["insertion"] = insertion
        time.sleep(0.11)
        runs += 1

    model.indicators["RMCS_INSERT"] = False

    model.indicators["RMCS_WITHDRAW"] = True


    #withdraw for 1.5 seconds
    runs = 0
    while runs < 15 and not model.rods[rod]["scram"]:
        insertion += 0.144
        model.rods[rod]["insertion"] = insertion
        time.sleep(0.11)
        runs += 1

    model.indicators["RMCS_WITHDRAW"] = False

    model.indicators["RMCS_SETTLE"] = True

    # TODO: simulate switching overlap between withdraw control and settle control

    #start the settle motion

    runs = 0
    while runs < 60 and not model.rods[rod]["scram"]:
        if insertion >= target_insertion:
            insertion = target_insertion
        else:
            insertion += 0.0064

        model.rods[rod]["insertion"] = insertion
        time.sleep(0.11)
        runs += 1

    if not model.rods[rod]["scram"]:
        model.rods[rod]["insertion"] = target_insertion

    model.rods[rod]["driving"] = False
    model.indicators["RMCS_SETTLE"] = False

def cont_withdraw_rod(rod:str):

    #check if this rod movement is valid first before starting the thread
    if reactor_protection_system.withdraw_block: 
        return

    from simulation.models.control_room_columbia import model

    current_rod = model.rods[rod]
    current_insertion = current_rod["insertion"]

    #TODO: overtravel test
    if int(current_insertion) >= 48:
        return
    
    motion = Thread(target=cont_withdraw_rod_motion,args=(rod,))
    motion.start()

def cont_withdraw_rod_motion(args):
    import time
    from simulation.models.control_room_columbia import model
    rod = args
    #time delay to insert control
    time.sleep(0.04)
    current_rod = model.rods[rod]
    current_insertion = current_rod["insertion"]
    model.rods[rod]["driving"] = True

    target_insertion = current_insertion+2

    model.indicators["RMCS_INSERT"] = True

    #insert (unlatch) for 0.6 seconds
    runs = 0
    while runs < 6:
        model.rods[rod]["insertion"] = model.rods[rod]["insertion"] - 0.082
        time.sleep(0.11)
        runs += 1

    model.indicators["RMCS_INSERT"] = False

    model.indicators["RMCS_WITHDRAW"] = True
    model.indicators["RMCS_CONT_WITHDRAW"] = True


    #withdraw for 1.5 seconds
    runs = 0
    while runs < 15:
        model.rods[rod]["insertion"] = model.rods[rod]["insertion"] + 0.144
        time.sleep(0.11)
        if model.buttons["RMCS_CONT_WITHDRAW_PB"]["state"] and runs >= 14 and not reactor_protection_system.withdraw_block:
            runs = 0
            model.rods[rod]["insertion"] = target_insertion
            target_insertion = model.rods[rod]["insertion"] + 2
        else:
            runs += 1

    model.indicators["RMCS_WITHDRAW"] = False
    model.indicators["RMCS_CONT_WITHDRAW"] = False

    model.indicators["RMCS_SETTLE"] = True

    # TODO: simulate switching overlap between withdraw control and settle control

    #start the settle motion

    runs = 0
    while runs < 60 and not model.rods[rod]["scram"]:
        if model.rods[rod]["insertion"] >= target_insertion:
            model.rods[rod]["insertion"] = target_insertion
        else:
            model.rods[rod]["insertion"] += 0.0064

        time.sleep(0.11)
        runs += 1

    if not model.rods[rod]["scram"]:
        model.rods[rod]["insertion"] = target_insertion

    model.rods[rod]["driving"] = False
    model.indicators["RMCS_SETTLE"] = False