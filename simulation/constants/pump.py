from simulation.models.control_room_columbia.general_physics import ac_power
from simulation.models.control_room_columbia.general_physics import fluid
import math
import log

def clamp(val, clamp_min, clamp_max):
    return min(max(val,clamp_min),clamp_max)


class MotorPump():
    def __init__(self,name="",motor_breaker_closed=False,bus="",horsepower=0,rated_rpm=1800,rated_discharge_press=0,rated_flow=0,current_limit=0,header="",suct_header="",loop_seq=False,custom=False):
        self.name = name
        self.motor_breaker_closed = motor_breaker_closed
        self.bus = bus
        self.horsepower = horsepower
        self.rated_rpm = rated_rpm
        self.rated_discharge_press = rated_discharge_press
        self.rated_flow = rated_flow
        self.current_limit = current_limit
        self.header = header
        self.suct_header = suct_header
        self.loop_seq = loop_seq
        self.custom = custom

    def start(self):
        self.motor_breaker_closed = True

    def stop(self):
        self.motor_breaker_closed = False

    def calculate_suction(self,delta):

        if self.suct_header== "":
            return self.flow
        #a
        #if pump["npshr"] < fluid.headers[pump["suct_header"]]["pressure"]*2.3072493927233:
        return self.flow

        return 0

    def calculate(self,delta):
        #undervoltage breaker trip

        voltage = 0
        #TODO: use the source classes in the valve stuff
        try:
            pump_bus = ac_power.busses[self.bus]

            voltage = pump_bus.voltage_at_bus()

            if voltage < 120 and self.motor_breaker_closed and not self.custom:
                self.motor_breaker_closed = False
                self.was_closed = True
                

            if not self.name in pump_bus.info["loads"]:
                pump_bus.register_load(self.watts,self.name )
            else:
                pump_bus.modify_load(self.watts,self.name )
        except:
            #log.warning("Pump does not have an available bus!")
            voltage = 4160

        if not self.custom:
            if self.loop_avail and self.was_closed:
                self.motor_breaker_closed = True
                self.was_closed = False

        target = 0

        if self.motor_breaker_closed:
            target = ((self.rated_rpm*(pump_bus.info["frequency"]/60))-self.rpm)
        else:
            target = -self.rpm

        Acceleration = (target)*1*delta

        self.rpm = clamp(self.rpm+Acceleration,0,self.rated_rpm+100)

        self.flow = self.rated_flow*(self.rpm/self.rated_rpm)
        self.flow = self.calculate_suction(delta)
        self.discharge_pressure = self.rated_discharge_press*(self.rpm/self.rated_rpm)

        if self.header != "":   
            self.actual_flow = fluid.inject_to_header(self.flow,self.discharge_pressure,fluid.headers[self.header]["temperature"],self.header,self.suct_header)
        else:
            self.actual_flow = self.flow

        #amps
            if voltage > 0 and self.motor_breaker_closed:
                AmpsFLA = (self.horsepower*746)/((math.sqrt(3)*voltage*0.876*0.95)) #TODO: variable motor efficiency and power factor

                self.amperes = (AmpsFLA*clamp(self.actual_flow/self.rated_flow,0.48,1))+(AmpsFLA*5*(Acceleration/(self.rated_rpm*1*delta)))
                self.watts = voltage*self.amperes*math.sqrt(3)
            else:
                self.amperes = 0
                self.watts = 0

class ShaftDrivenPump():
    def __init__(self,rated_rpm,rated_discharge_press,rated_flow,header,suct_header):
        self.rated_rpm = rated_rpm
        self.rated_discharge_press =rated_discharge_press
        self.rated_flow = rated_flow
        self.header = header
        self.suct_header = suct_header
        self.rpm = 0

    def set_rpm(self,rpm):
        self.rpm = rpm

    def calculate_suction(self,delta):

        if self.suct_header== "":
            return self.flow
        #a
        #if pump["npshr"] < fluid.headers[pump["suct_header"]]["pressure"]*2.3072493927233:
        return self.flow

        return 0

    def calculate(self,delta):

        self.flow = self.rated_flow*(self.rpm/self.rated_rpm)
        self.flow = self.calculate_suction(delta)
        self.discharge_pressure = self.rated_discharge_press*(self.rpm/self.rated_rpm)
            
        self.actual_flow = fluid.inject_to_header(self.flow,self.discharge_pressure,fluid.headers[self.header]["temperature"],self.header,self.suct_header)
    

