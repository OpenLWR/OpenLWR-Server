#Control And Service air system
from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.general_physics import air_system as air
from simulation.models.control_room_columbia.general_physics import ac_power

STANDBY_AIR_COMP_TIMER = 0 #30 minutes runtime
STANDBY_AIR_COMP_START_PRESS = 100 #psig
STANDBY_AIR_COMP_STOP_PRESS = 105 #psig

CAS_C_1A = None
CAS_C_1B = None
CAS_C_1C = None

CAS_AR_1A = None #Air Receiver

CONTROL_AIR_HEADER = None
SCRAM_AIR_HEADER = None

CRD_SCRAM_ISOLATE = None #simplified version
CRD_SCRAM_VENT = None #simplified version

CRD_ATWS_ISOLATE = None #Simplified
CRD_ATWS_VENT = None #Simplified

SA_PCV_2 = None #SA - CAS Crosstie Isolation (auto)

VENT = None


def init():

    global STANDBY_AIR_COMP_TIMER
    global STANDBY_AIR_COMP_START_PRESS
    global STANDBY_AIR_COMP_STOP_PRESS

    global CAS_C_1A
    global CAS_C_1B
    global CAS_C_1C

    global CAS_AR_1A

    global CONTROL_AIR_HEADER

    CONTROL_AIR_HEADER = air.AirHeader(1,120,2)

    CAS_C_1A = air.Compressor(130,air.SupplyElectric(ac_power.busses["7a"],240,None),100)
    CAS_C_1B = air.Compressor(130,air.SupplyElectric(ac_power.busses["8a"],240,None),100) 
    CAS_C_1C = air.Compressor(130,air.SupplyElectric(ac_power.busses["2p"],240,None),100) #MC-2P (off of SL-21 TB MEZZANINE)

    CAS_C_1A.add_loading_system(110,120,CONTROL_AIR_HEADER)
    CAS_C_1B.add_loading_system(110,120,CONTROL_AIR_HEADER)
    CAS_C_1C.add_loading_system(110,120,CONTROL_AIR_HEADER)

    CAS_AR_1A = air.AirHeader(1,120,15) #there is actually multiple but just one is good enough simulation wise

    CAS_AR_1A.add_feeder(CAS_C_1A)
    CAS_AR_1A.add_feeder(CAS_C_1B)
    CAS_AR_1A.add_feeder(CAS_C_1C)

    CONTROL_AIR_HEADER.add_feeder(CAS_AR_1A)

    global SCRAM_AIR_HEADER
    global CRD_SCRAM_ISOLATE
    global CRD_SCRAM_VENT
    global CRD_ATWS_ISOLATE
    global CRD_ATWS_VENT
    global VENT

    SCRAM_AIR_HEADER = air.AirHeader(1,120,0.2) #what is the actual normal pressure?
    CRD_SCRAM_ISOLATE = air.Valve(100,None,False,False,500)
    CRD_SCRAM_VENT = air.Valve(0,None,False,False,500)

    SCRAM_AIR_HEADER.add_feeder(CONTROL_AIR_HEADER,CRD_SCRAM_ISOLATE)
    VENT = air.Vent()
    VENT.add_feeder(SCRAM_AIR_HEADER,CRD_SCRAM_VENT)

def run():
    global STANDBY_AIR_COMP_TIMER
    CAS_C_1A_STANDBY = False
    CAS_C_1B_STANDBY = False
    CAS_C_1C_STANDBY = False

    CONTROL_AIR_HEADER.calculate()
    CAS_AR_1A.calculate()
    SCRAM_AIR_HEADER.calculate()
    VENT.calculate()
    CAS_C_1A.calculate()
    CAS_C_1B.calculate()
    CAS_C_1C.calculate()

    model.switches["cas_c_1a"]["lights"]["red"] = CAS_C_1A.motor_breaker_closed
    model.switches["cas_c_1a"]["lights"]["green"] = not CAS_C_1A.motor_breaker_closed
    model.switches["cas_c_1a"]["lights"]["unloaded"] = CAS_C_1A.unloaded

    model.switches["cas_c_1b"]["lights"]["red"] = CAS_C_1B.motor_breaker_closed
    model.switches["cas_c_1b"]["lights"]["green"] = not CAS_C_1B.motor_breaker_closed
    model.switches["cas_c_1b"]["lights"]["unloaded"] = CAS_C_1B.unloaded

    model.switches["cas_c_1c"]["lights"]["red"] = CAS_C_1C.motor_breaker_closed
    model.switches["cas_c_1c"]["lights"]["green"] = not CAS_C_1C.motor_breaker_closed
    model.switches["cas_c_1c"]["lights"]["unloaded"] = CAS_C_1C.unloaded

    match model.switches["cas_c_1a"]["position"]:
        case 0:
            CAS_C_1A.stop()
        case 1:
            CAS_C_1A_STANDBY = True
        case 2:
            CAS_C_1A.start()

    match model.switches["cas_c_1b"]["position"]:
        case 0:
            CAS_C_1B.stop()
        case 1:
            CAS_C_1B_STANDBY = True
        case 2:
            CAS_C_1B.start()

    match model.switches["cas_c_1c"]["position"]:
        case 0:
            CAS_C_1C.stop()
        case 1:
            CAS_C_1C_STANDBY = True
        case 2:
            CAS_C_1C.start()
        

    if STANDBY_AIR_COMP_TIMER >= 30*60*10 and STANDBY_AIR_COMP_STOP_PRESS < CONTROL_AIR_HEADER.get_pressure():
        model.alarms["standby_air_comp_on"]["alarm"] = False
        if STANDBY_AIR_COMP_TIMER > 0:
            #Stop standby comps
            if CAS_C_1A_STANDBY:
                CAS_C_1A.stop()
            if CAS_C_1B_STANDBY:
                CAS_C_1B.stop()
            if CAS_C_1C_STANDBY:
                CAS_C_1C.stop()

        STANDBY_AIR_COMP_TIMER = 0


    if CONTROL_AIR_HEADER.get_pressure() < STANDBY_AIR_COMP_START_PRESS or STANDBY_AIR_COMP_TIMER > 0:
        model.alarms["standby_air_comp_on"]["alarm"] = True
        
        if STANDBY_AIR_COMP_TIMER == 0:
            #Start standby comps
            if CAS_C_1A_STANDBY:
                CAS_C_1A.start()
            if CAS_C_1B_STANDBY:
                CAS_C_1B.start()
            if CAS_C_1C_STANDBY:
                CAS_C_1C.start()

        STANDBY_AIR_COMP_TIMER += 1

    CONTROL_AIR_HEADER.fill -= 0.0001 #fixed leak rate

    if CONTROL_AIR_HEADER.get_pressure() < 90: #isolate SA and trigger low press alarm
        model.alarms["control_air_hdr_press_low"]["alarm"] = True
    else:
        model.alarms["control_air_hdr_press_low"]["alarm"] = False

    model.alarms["scram_valve_pilot_air_header_press_low"]["alarm"] = SCRAM_AIR_HEADER.get_pressure() < 95

    model.values["control_air_press"] = CONTROL_AIR_HEADER.get_pressure()
