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

    def get_pressure(self):
        return self.fill * self.normal_pressure

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