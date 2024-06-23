import math
from simulation.models.control_room_columbia import reactor_protection_system
from simulation.models.control_room_columbia import model
from threading import Thread
any_rod_driving = False
select_block = False

def run(rods,buttons):
    any_rod_driving = False
    global select_block

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
            elif buttons["RMCS_WITHDRAW_PB"]["state"]:
                withdraw_rod(rod)



        if info["scram"]:
            #TODO: accumulator pressure and its affect on rod drive
            if info["insertion"] > 0:
                info["insertion"] = info["insertion"] - 1.6 #approximately 3 seconds to scram from full out
                info["accum_pressure"] = info["accum_pressure"] - 30 #approximately 2 seconds until the accumulator alarm activates
            else:
                info["insertion"] = 0

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

    #TODO: holding down "insert" inserts the rod for however long its pressed, but still end with a settle sequence.
    #This is different from continuous insert, as that does not have a settle sequence.
    
    #insert the rod for 2.9 seconds
    runs = 0
    while runs < 29 and not model.rods[rod]["scram"]:
        insertion -= 0.082
        model.rods[rod]["insertion"] = insertion
        time.sleep(0.11)
        runs += 1

    model.indicators["RMCS_INSERT"] = False

    model.indicators["RMCS_SETTLE"] = True

    #start the settle motion

    runs = 0
    while runs < 53 and not model.rods[rod]["scram"]:
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