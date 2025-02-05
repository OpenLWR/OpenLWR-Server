from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.general_physics import air_system as air

Mainheader = None
MainheaderDrywell = None
ADSAHeader = None
ADSBHeader = None

CIA_V_39A = None
CIA_V_39B = None
CIA_V_30A = None
CIA_V_30B = None
CIA_V_20 = None

ISOLTIMER = 0

def init():
    global Mainheader
    global MainheaderDrywell
    global ADSAHeader
    global ADSBHeader

    global CIA_V_39A
    global CIA_V_39B
    global CIA_V_30A
    global CIA_V_30B
    global CIA_V_20

    Mainheader = air.AirHeader(1,185)
    MainheaderDrywell = air.AirHeader(1,185)
    ADSAHeader = air.AirHeader(1,180)
    ADSBHeader = air.AirHeader(1,180)

    CIA_V_39A = air.Valve(100,"cia_v_39a",True,True,50,air.SupplyAir(Mainheader,60,air.FailureModes.CLOSED))
    CIA_V_39B = air.Valve(100,None,True,True,50,air.SupplyAir(Mainheader,60,air.FailureModes.CLOSED))
    CIA_V_30A = air.Valve(100,"cia_v_30a",True,True,15,None) #supply is electric
    CIA_V_30B = air.Valve(100,None,True,True,15,None) #supply is electric
    CIA_V_20 = air.Valve(100,"cia_v_20",True,True,15,None) #supply is electric

    ADSAHeader.add_feeder(Mainheader,CIA_V_39A)
    ADSBHeader.add_feeder(Mainheader,CIA_V_39B)
    MainheaderDrywell.add_feeder(Mainheader,CIA_V_20)

DIV1MANOOS = False
DIV1MANOOSP = False #was pressed, prevents crazy lights

def run():

    global ISOLTIMER
    global DIV1MANOOS
    global DIV1MANOOSP

    Mainheader.calculate()
    MainheaderDrywell.calculate()
    ADSAHeader.calculate()
    ADSBHeader.calculate()

    CIA_V_39A.calculate()
    CIA_V_39B.calculate()
    CIA_V_30A.calculate()
    CIA_V_30B.calculate()
    CIA_V_20.calculate()

    if Mainheader.get_pressure() < 160: #isolate at 160
        if ISOLTIMER < 180: #time delay prevents spurious actuation for temporary high flow rates
            ISOLTIMER += 0.1
        else:
            model.alarms["ads_n2_hdr_a_isolated"]["alarm"] = True
            CIA_V_39A.close()
            CIA_V_39B.close()
    else:
        if ISOLTIMER > 0:
            model.alarms["ads_n2_hdr_a_isolated"]["alarm"] = False
            ISOLTIMER = 0
            CIA_V_39A.open()
            CIA_V_39B.open()

    DIV1OOS = DIV1MANOOS
    BISI1TEST = model.buttons["cia_a_lamp_test"]["state"]
    
    if model.buttons["cia_a_manual_out_of_serv"]["state"] and not DIV1MANOOSP:
        DIV1MANOOSP = True
        DIV1MANOOS = not DIV1MANOOS
    elif model.buttons["cia_a_manual_out_of_serv"]["state"] == False:
        DIV1MANOOSP = False

    model.alarms["cia_a_manual_out_of_serv"]["alarm"] = DIV1MANOOS or BISI1TEST

    if ADSAHeader.get_pressure() < 156:
        model.alarms["n2_div_1_supply_press_low"]["alarm"] = True
        #TODO: Bottles and programmers
        DIV1OOS = True
    else:
        model.alarms["n2_div_1_supply_press_low"]["alarm"] = BISI1TEST


    

    model.alarms["cia_div_1_out_of_serv"]["alarm"] = DIV1OOS

    model.values["cia_main_header_press"] = Mainheader.get_pressure()
    model.values["cia_ads_a_header_press"] = ADSAHeader.get_pressure()

    #TODO: Div 2 BISI

    

    
    
            