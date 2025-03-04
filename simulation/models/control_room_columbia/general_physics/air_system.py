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
    
class SupplyElectric():
    def __init__(self,bus,failure_voltage,failure_mode):
        self.bus = bus
        self.failure_voltage = failure_voltage
        self.failure_mode = failure_mode

    def check_available(self):
        return self.bus.is_voltage_at_bus(self.failure_voltage)

class PressureControlValve:
    def __init__(self,percent_open,header,normal_pressure,band=10):
        self.percent_open = percent_open
        self.header = header
        self.normal_pressure = normal_pressure
        self.band = band

    def calculate(self):
        self.percent_open = min(max(((self.normal_pressure-self.header.get_pressure())/self.band)*100,0),100)

class Valve:
    def __init__(self,percent_open,switch_name=None,seal_in=False,sealed_in=False,open_speed=0,supply = None,drop_indication_on_motive_lost = False, only_indicate = False,):
        self.percent_open = percent_open
        self.switch_name = switch_name
        self.seal_in = seal_in
        self.sealed_in = sealed_in
        self.open_speed = open_speed*0.1
        self.supply = supply
        self.drop_indication_on_motive_lost = drop_indication_on_motive_lost
        self.only_indicate = only_indicate

    def stroke_open(self,speed=None):
        if speed == None:
            speed = self.open_speed

        self.percent_open = min(max(self.percent_open+speed,0),100)

    def stroke_closed(self,speed=None):
        if speed == None:
            speed = self.open_speed

        self.percent_open = min(max(self.percent_open-speed,0),100)

    def close(self):
        self.sealed_in = False
    
    def open(self):
        self.sealed_in = True

    def get_switch_position(self):
        if self.switch_name not in model.switches:
            return False
        
        return model.switches[self.switch_name]["position"]

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

            if available == False or self.only_indicate:
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
    def __init__(self,fill,normal_pressure,size=1):
        self.fill = fill
        self.normal_pressure = normal_pressure #PSIG
        self.size=size #allows making some headers bigger than others, like tanks and whatnot
        self.feeders = []

    def add_feeder(self,header,valve=None,isolation_valve=None):
        self.feeders.append({"header":header,"valve":valve,"isolation":isolation_valve,})

    def get_pressure(self):
        return self.fill * self.normal_pressure

    def calculate(self):
        Press = self.fill * self.normal_pressure
        Total_Flow = 0


        for feed in self.feeders:
            DeltaP = (feed["header"].fill * feed["header"].normal_pressure) - Press

            Flow = DeltaP/self.normal_pressure
            Flow = Flow*0.0035

            if feed["valve"] != None:
                Flow = Flow*feed["valve"].percent_open

            if feed["isolation"] != None:
                Flow = Flow*(feed["isolation"].percent_open/100)

            Total_Flow += Flow

            feed["header"].fill -= ((Flow*self.normal_pressure)/feed["header"].normal_pressure)/feed["header"].size#/len(self.feeders)

        if len(self.feeders) == 0:
            return

        #Total_Flow /= len(self.feeders)

        self.fill += Total_Flow/self.size

class Vent:
    def __init__(self):
        self.fill = 1
        self.normal_pressure = 14.7 #PSIG
        self.size = 1
        self.feeders = []

    def add_feeder(self,header,valve=None):
        self.feeders.append({"header":header,"valve":valve})

    def get_pressure(self):
        return self.fill * self.normal_pressure

    def calculate(self):
        Press = self.fill * self.normal_pressure


        for feed in self.feeders:
            DeltaP = (feed["header"].fill * feed["header"].normal_pressure) - Press

            Flow = DeltaP/self.normal_pressure
            Flow = Flow*0.001

            if feed["valve"] != None:
                Flow = Flow*feed["valve"].percent_open

            feed["header"].fill -= ((Flow*self.normal_pressure)/feed["header"].normal_pressure)#/len(self.feeders)

class Compressor():
    def __init__(self,discharge_pressure,supply,horsepower):
        self.fill = 1
        self.size = 1
        self.normal_pressure = discharge_pressure #these emulate a header, so there is less code copied around

        self.motor_breaker_closed = False
        #assert supply in SupplyElectric, "You cant use air to move air wtf"
        self.supply = supply
        self.horespower = horsepower #used to calculate LRA and FLA

        self.has_loading_system = False
        self.band_low = 0
        self.band_high = 0
        self.unloaded = False
        self.pressure_reference = None

    def stop(self):
        self.motor_breaker_closed = False
    
    def start(self):
        self.motor_breaker_closed = True

    def add_loading_system(self,band_low,band_high,pressure_reference = None):
        self.has_loading_system = True
        self.band_low = band_low
        self.band_high = band_high

        if pressure_reference == None:
            pressure_reference = self

        self.pressure_reference = pressure_reference

    def loading_system(self):
        #Simple P controller
        Band = self.band_high - self.band_low 
        Press = self.pressure_reference.fill * self.pressure_reference.normal_pressure
        Demand = min(max((self.band_high - Press) / Band,0),1)
        Demand *= 100

        self.unloaded = Demand <= 25 #i dont really know what this is supposed to be at
        return min(max(Demand,0),100)

    def calculate(self):
        self.fill = max(self.fill,0)
        if self.motor_breaker_closed and self.supply.check_available():
            accel = 0.05

            if self.has_loading_system:
                accel = accel * (self.loading_system()/100)

            self.fill += (1-self.fill)*accel
        else:
            self.unloaded = False
            
            


            

