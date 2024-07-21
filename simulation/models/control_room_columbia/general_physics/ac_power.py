from simulation.constants.electrical_types import ElectricalType
from simulation.constants.equipment_states import EquipmentStates
from simulation.models.control_room_columbia.general_physics import diesel_generator
from simulation.models.control_room_columbia import model
import math
import log

def calculate_phase(frequency,phase):
    #hertz is number of revolutions per second
    #so at 60hz, we revolve 60 times
    phase = phase+((frequency*360)*0.1) #make 0.1 the execution time instead

    if phase >= 360:
        mul = math.floor(phase/360)
        phase = phase-(360*mul) #is this the correct way to do this?

    return phase

sources = {}
busses = {}
breakers = {}

class Source:
    def __init__(self,name="",voltage=0,frequency=0,phase=0,annunciators={}):
        self.name = name
        self.info = {
            "type" : ElectricalType.SOURCE,
            "voltage" : voltage,
            "frequency" : frequency,
            "phase" : phase,
            "loads" : {},

            "annunciators" : annunciators
        }
        sources[name] = self

    def whoami(self):
        return self.__class__
    
    def get_source(self):
        """bro its us"""
        return self
    
    def calculate(self):
        self.info["phase"] = calculate_phase(self.info["frequency"],self.info["phase"])

    def register_load(self,load,name):
        """Registers a load on this bus, with the specified load in watts."""
        if not name in self.info["loads"]:
            x = self.info["loads"].copy()
            x[name] = load
            y = x
            self.info["loads"] = y

    def modify_load(self,load,name):
        """Modifies an existing load on this bus, with the new specified load in watts."""
        if name in self.info["loads"]:
            x = self.info["loads"].copy()
            x[name] = load
            y = x
            self.info["loads"] = y

    def remove_load(self,name):
        """Removes an existing load on this bus."""
        if name in self.info["loads"]:
            x = self.info["loads"].copy()
            x.pop(name)
            y = x
            self.info["loads"] = y

class Bus:
    def __init__(self,name="",voltage=0,frequency=0,current=0,phase=0,loads={},feeders=[],rated_voltage=0,lockout=False,source_breakers=[],annunciators={}):
        self.name = name
        self.info = {
            "type" : ElectricalType.BUS, #TODO: Do we need this anymore?
            "voltage" : voltage,
            "frequency" : frequency,
            "current" : current,
            "phase" : phase,
            "loads" : loads,
            "feeders" : feeders,

            "rated_voltage" : rated_voltage,

            "lockout" : lockout, #ANY source breaker is locked out (prevents re-energizing a faulted bus)
            "source_breakers" : source_breakers, #TODO: Re-implement this

            "annunciators" : annunciators,
        }
        busses[name] = self

    def whoami(self):
        return self.__class__

    def get_source(self):
        """we are the source"""
        return self
    
    def register_feeder(self,feeder):
        if not feeder in self.info["feeders"]:
            x = self.info["feeders"] #workaround for some random bug
            y = x + [feeder]
            self.info["feeders"] = y

    def calculate(self):
        all_feeder_info = []

        total_load = 0

        for load in self.info["loads"]:
            total_load += self.info["loads"][load]

        #TODO: Distribute loads properly while paralleling
        for feeder in self.info["feeders"]:
            if True:
                source = feeder.get_source()

                if feeder.get_source(closed_check = True) == False:
                    self.info["feeders"].remove(feeder)
                    source.remove_load(self.name)

                all_feeder_info.append(source)

                if not self.name in source.info["loads"]:
                    source.register_load(total_load,self.name)
                else:
                    source.modify_load(total_load,self.name)

            
        voltage = 0
        frequency = 0
        phase = 0
        for info in all_feeder_info:
            voltage = max(voltage,info.info["voltage"])
            if frequency < info.info["frequency"]:
                frequency = info.info["frequency"]
                phase = info.info["phase"]

        self.info["voltage"] = voltage
        self.info["frequency"] = frequency
        self.info["phase"] = phase

    def voltage_at_bus(self):
        """Gets the current voltage at the bus. Will be a number."""
        return self.info["voltage"]
    
    def is_voltage_at_bus(self,setpoint):
        """Gets if voltage is present at the bus. Takes a undervoltage setpoint."""

        return self.info["voltage"] > setpoint
    
    def register_load(self,load,name):
        """Registers a load on this bus, with the specified load in watts."""
        if not name in self.info["loads"]:
            x = self.info["loads"].copy()
            x[name] = load
            y = x
            self.info["loads"] = y

    def modify_load(self,load,name):
        """Modifies an existing load on this bus, with the new specified load in watts."""
        if name in self.info["loads"]:
            x = self.info["loads"].copy()
            x[name] = load
            y = x
            self.info["loads"] = y

    def remove_load(self,name):
        """Removes an existing load on this bus."""
        if name in self.info["loads"]:
            x = self.info["loads"].copy()
            x.pop(name)
            y = x
            self.info["loads"] = y
            

class Breaker:
    def __init__(self,name="",cs="",closed=False,incoming=None,running=None,lockout=False,ptl=False,current_limit=12.5,custom=False):
        self.name = name
        if cs == "":
            cs = name
        self.info = {
            "type" : ElectricalType.BREAKER, #TODO: Do we need this anymore?
            "control_switch" : cs,
		    "closed" : closed,
		    "incoming" : incoming,
		    "running" : running, 
		    "lockout" : lockout, #Breaker lockout relay tripped
            "ptl" : ptl, #Pull To Lock
            "sync_sel" : False, #Has a sync selector
            "sync" : False, #Sync Selector in MAN
	        "flag_position" : False,
            "custom" : custom,

            "current_limit" : current_limit, #amps 
        }
        breakers[name] = self

    def whoami(self):
        return self.__class__
    
    def set_incoming(self,object):
        self.info["incoming"] = object

    def set_running(self,object):
        self.info["running"] = object

    def close(self):
        """Closes the breaker."""
        #TODO: breakers failing to close
        self.info["closed"] = True and not self.info["lockout"]

    def open(self):
        """Opens the breaker."""
        #TODO: breakers failing to open
        self.info["closed"] = False

    def get_source(self,closed_check = False):
        """Gets the 'source' for the breaker.
        This would either be an actual source type, a bus, or a transformer.
        Returns the source object.
        Optionally returns if all breakers on that path are closed."""
        source = None
        closed = self.info["closed"]
        while True:
            if source == None:
                source = self.info["incoming"]

            if source.whoami() == Breaker:
                if not source.info["closed"]:
                    closed = False

            if source.whoami() == Bus:
                break
            elif source.whoami() == Source:
                break
            else:
                source = source.info["incoming"]

        value = source

        if closed_check == True:
            value = closed

        return value
    
    def breaker_switch(self):
        """Default behavior for breaker switches. Can be disabled by setting 'custom' on init"""
        if self.info["custom"]: return

        if self.info["control_switch"] != "":
            if model.switches[self.info["control_switch"]]["position"] == 0: self.open()

            if model.switches[self.info["control_switch"]]["position"] == 2 and (self.info["sync_sel"] == False or self.info["sync"] == True): self.close()

            model.switches[self.info["control_switch"]]["lights"]["green"] = not self.info["closed"]
            model.switches[self.info["control_switch"]]["lights"]["red"] = self.info["closed"]

            #TODO: Sync Permit

            if "lockout" in model.switches[self.info["control_switch"]]["lights"]:
                model.switches[self.info["control_switch"]]["lights"]["lockout"] = not self.info["lockout"]

    
    def calculate(self):
        self.breaker_switch()
        if self.info["running"].whoami() == Bus:
            if self.get_source(closed_check=True):
                self.info["running"].register_feeder(self)





#TODO: Transformers

def initialize():
    Source(name="TRS",voltage=4160,frequency=60) #TODO: Make this an actual transformer
    Source(name="DG1",voltage=0,frequency=0)
    Source(name="DG2",voltage=0,frequency=0)
    Source(name="GRID",voltage=25000,frequency=60) #change from 25 to 500 (or normal grid voltage?)
    Source(name="GEN",voltage=0,frequency=0)

    Bus(name="gen_bus",voltage=0,frequency=0,rated_voltage=25000)

    Bus(name="1",voltage=4160,frequency=60,rated_voltage=4160)
    Bus(name="2",voltage=4160,frequency=60,rated_voltage=4160)
    Bus(name="3",voltage=4160,frequency=60,rated_voltage=4160)

    Bus(name="5",voltage=6900,frequency=60,rated_voltage=6900)
    Bus(name="6",voltage=6900,frequency=60,rated_voltage=6900)

    Bus(name="7",voltage=4160,frequency=60,rated_voltage=4160)
    Bus(name="4",voltage=4160,frequency=60,rated_voltage=4160)
    Bus(name="8",voltage=4160,frequency=60,rated_voltage=4160)
    

    Breaker(name="cb_s1",incoming=sources["TRS"],running=busses["1"],closed=True)
    Breaker(name="cb_s2",incoming=sources["TRS"],running=busses["2"],closed=True)
    Breaker(name="cb_s3",incoming=sources["TRS"],running=busses["3"],closed=True)

    Breaker(name="cb_1_7",incoming=busses["1"],closed=True)
    Breaker(name="cb_7_1",incoming=breakers["cb_1_7"],running=busses["7"],closed=True)

    breakers["cb_1_7"].set_running(breakers["cb_7_1"])

    #DG1

    Breaker(name="cb_dg1_7",incoming=sources["DG1"])
    Breaker(name="cb_7dg1",incoming=breakers["cb_dg1_7"],running=busses["7"],closed=True)

    breakers["cb_dg1_7"].set_running(breakers["cb_7dg1"])

    Breaker(name="cb_3_8",incoming=busses["3"],closed=True)
    Breaker(name="cb_8_3",incoming=breakers["cb_3_8"],running=busses["8"],closed=True)

    breakers["cb_3_8"].set_running(breakers["cb_8_3"])

    #DG2

    Breaker(name="cb_dg2_8",incoming=sources["DG2"])
    Breaker(name="cb_8dg2",incoming=breakers["cb_dg2_8"],running=busses["8"],closed=True)

    breakers["cb_dg2_8"].set_running(breakers["cb_8dg2"])

    Breaker(name="gen_output",incoming=sources["GEN"],running=busses["gen_bus"],closed=True,custom=True)

    Breaker(name="cb_4445",incoming=sources["GRID"],running=busses["gen_bus"],closed=True)

    Breaker(name="cb_4448",incoming=sources["GRID"],running=busses["gen_bus"],closed=True)

def run():

    global graph

    #TODO: Move elsewhere

    model.indicators["cr_light_normal_1"] = busses["7"].is_voltage_at_bus(3000)
    model.indicators["cr_light_normal_2"] = busses["8"].is_voltage_at_bus(3000)
    model.indicators["cr_light_emergency"] = not (busses["7"].is_voltage_at_bus(3000) and busses["8"].is_voltage_at_bus(3000)) #TODO: divisional emergency lights

    for source in sources:
        source = sources[source]
        source.calculate()

    for breaker in breakers:
        breaker = breakers[breaker]
        breaker.calculate()

    for bus in busses:
        bus = busses[bus]
        bus.calculate()

    #This loop is ONLY for logic!
    for bus in busses:
        bus = busses[bus]
        #Primary undervoltage 
        if bus.info["voltage"]/bus.info["rated_voltage"] < 0.69:
            #TODO: load shedding

            #TODO: Backup Transformer

            if bus.name == "7":
                diesel_generator.dg1.start(auto = True)

                if diesel_generator.dg1.dg["voltage"] >= 4160:
                    breakers["cb_dg1_7"].close()

                breakers["cb_7_1"].open()

            if bus.name == "8":
                diesel_generator.dg2.start(auto = True)

                if diesel_generator.dg2.dg["voltage"] >= 4160:
                    breakers["cb_dg2_8"].close()

                breakers["cb_8_3"].open()


    #TODO: Secondary undervoltage
