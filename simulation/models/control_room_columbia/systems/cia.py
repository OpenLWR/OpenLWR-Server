from simulation.models.control_room_columbia import model

from enum import IntEnum

class FailureModes(IntEnum):
    AS_IS = 0,
    CLOSED = 1,
    OPEN = 2,

class SupplyAir():
    def __init__(self,header,failure_pressure,failure_mode):
        self.header = header
        self.failure_pressure = failure_pressure
        self.failure_mode = failure_mode

    def check_available(self):
        return self.header.fill * self.header.normal_pressure > self.failure_pressure

class Valve:
    def __init__(self,percent_open,switch_name,seal_in,sealed_in,open_speed,supply = None):
        self.percent_open = percent_open
        self.switch_name = switch_name
        self.seal_in = seal_in
        self.sealed_in = sealed_in
        self.open_speed = open_speed*0.1
        self.supply = supply
        self.drop_indication_on_motive_lost = False

    def stroke_open(self):
        self.percent_open = min(max(self.percent_open+self.open_speed,0),100)

    def stroke_closed(self):
        self.percent_open = min(max(self.percent_open-self.open_speed,0),100)

    def close(self):
        self.sealed_in = False
    
    def open(self):
        self.sealed_in = True

    def calculate(self):
        if self.switch_name != None:
            switch = model.switches[self.switch_name]

            available = True
            if self.supply != None:
                available = self.supply.check_available()
                if available == False:
                    match self.supply.failure_mode:
                        case FailureModes.CLOSED:
                            self.stroke_closed()
                        case FailureModes.OPEN:
                            self.stroke_open()

            if switch["lights"] != {}:
                switch["lights"]["green"] = self.percent_open < 100
                switch["lights"]["red"] = self.percent_open > 0

            if available == False:
                return

            if not self.seal_in:
                if switch["position"] == 2:
                    self.stroke_open()
                elif switch["position"] == 0:
                    self.stroke_closed()
            else:
                if len(switch["positions"]) < 3:
                    if switch["position"] == 1:
                        self.sealed_in = True
                    elif switch["position"] == 0:
                        self.sealed_in = False
                else:
                    if switch["position"] == 2:
                        self.sealed_in = True
                    elif switch["position"] == 0:
                        self.sealed_in = False

                if self.sealed_in:
                    self.stroke_open()
                else:
                    self.stroke_closed()
                  
class AirHeader:
    def __init__(self,fill,normal_pressure):
        self.fill = fill
        self.normal_pressure = normal_pressure #PSIG
        self.feeders = []

    def add_feeder(self,header,valve):
        self.feeders.append({"header":header,"valve":valve})

    def calculate(self):
        Press = self.fill * self.normal_pressure
        Total_Flow = 0


        for feed in self.feeders:
            DeltaP = (feed["header"].fill * feed["header"].normal_pressure) - Press

            Flow = DeltaP/self.normal_pressure
            Flow = Flow*0.001
            Flow = Flow*feed["valve"].percent_open

            Total_Flow += Flow

            feed["header"].fill -= ((Flow*self.normal_pressure)/feed["header"].normal_pressure)/len(self.feeders)

        if len(self.feeders) == 0:
            return

        Total_Flow /= len(self.feeders)

        self.fill += Total_Flow

#TODO: Move all of the above to a different file
Mainheader = None
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
    global ADSAHeader
    global ADSBHeader

    global CIA_V_39A
    global CIA_V_39B
    global CIA_V_30A
    global CIA_V_30B
    global CIA_V_20

    Mainheader = AirHeader(1,185)
    ADSAHeader = AirHeader(1,180)
    ADSBHeader = AirHeader(1,180)

    CIA_V_39A = Valve(100,"cia_v_39a",True,True,50,SupplyAir(Mainheader,60,FailureModes.CLOSED))
    CIA_V_39B = Valve(100,None,True,True,50,SupplyAir(Mainheader,60,FailureModes.CLOSED))
    CIA_V_30A = Valve(100,"cia_v_30a",True,True,15,None) #supply is electric
    CIA_V_30B = Valve(100,None,True,True,15,None) #supply is electric
    CIA_V_20 = Valve(100,"cia_v_20",True,True,15,None) #supply is electric

    ADSAHeader.add_feeder(Mainheader,CIA_V_39A)
    ADSBHeader.add_feeder(Mainheader,CIA_V_39B)

DIV1MANOOS = False
DIV1MANOOSP = False #was pressed, prevents crazy lights

def run():

    global ISOLTIMER
    global DIV1MANOOS
    global DIV1MANOOSP

    Mainheader.calculate()
    ADSAHeader.calculate()
    ADSBHeader.calculate()

    CIA_V_39A.calculate()
    CIA_V_39B.calculate()
    CIA_V_30A.calculate()
    CIA_V_30B.calculate()
    CIA_V_20.calculate()

    if Mainheader.fill * Mainheader.normal_pressure < 160: #isolate at 160
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

    if ADSAHeader.fill * ADSAHeader.normal_pressure < 156:
        model.alarms["n2_div_1_supply_press_low"]["alarm"] = True
        #TODO: Bottles and programmers
        DIV1OOS = True
    else:
        model.alarms["n2_div_1_supply_press_low"]["alarm"] = BISI1TEST


    

    model.alarms["cia_div_1_out_of_serv"]["alarm"] = DIV1OOS

    model.values["cia_main_header_press"] = Mainheader.fill * Mainheader.normal_pressure
    model.values["cia_ads_a_header_press"] = ADSAHeader.fill * ADSAHeader.normal_pressure

    #TODO: Div 2 BISI

    

    
    
            