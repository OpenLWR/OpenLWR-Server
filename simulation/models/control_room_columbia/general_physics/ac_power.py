from simulation.constants.electrical_types import ElectricalType
from simulation.constants.equipment_states import EquipmentStates
from simulation.models.control_room_columbia.general_physics import diesel_generator
from simulation.models.control_room_columbia import model
#from simulation.models.control_room_columbia.libraries import transient
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
transformers = {}

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
            if feeder.whoami() == Breaker:
                source = feeder.get_source()

                if feeder.get_source(closed_check = True) == False:
                    self.info["feeders"].remove(feeder)
                    source.remove_load(self.name)

                all_feeder_info.append(source)

                if not self.name in source.info["loads"]:
                    source.register_load(total_load,self.name)
                else:
                    source.modify_load(total_load,self.name)

            elif feeder.whoami() == Transformer:
                source = feeder.get_source()

                if feeder.get_source(closed_check = True) == False:
                    self.info["feeders"].remove(feeder)
                    source.remove_load(self.name)

                all_feeder_info.append(feeder)

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

            "current" : 0, #amps
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

            if "sync" in model.switches[self.info["control_switch"]]["lights"]:
                model.switches[self.info["control_switch"]]["lights"]["sync"] = self.info["sync"] #TODO: Make this illuminate only from time of taking to close to breaker closure

            self.info["sync"] = False

    
    def calculate(self):
        self.breaker_switch()
        if self.info["running"].whoami() == Bus:
            if self.get_source(closed_check=True):
                self.info["running"].register_feeder(self)
                
                total_load = 0
                for load in self.info["running"].info["loads"]:
                    total_load += self.info["running"].info["loads"][load]

                self.info["current"] = total_load/(self.info["running"].info["voltage"]+0.1)

class Transformer:
    def __init__(self,name="",incoming=None,running=None,lockout=False,factor=1,voltage=0,frequency=0,current_limit=12.5):
        self.name = name
        self.info = {
            "type" : ElectricalType.TRANSFORMER, #TODO: Do we need this anymore?
		    "incoming" : incoming,
		    "running" : running, 
		    "lockout" : lockout, #Transformer lockout 

            "voltage" : voltage,
            "frequency" : frequency,
            "phase" : 0,
            "factor" : factor,
            "current" : 0, #amps
            "current_limit" : current_limit, #amps 
        }
        transformers[name] = self

    def whoami(self):
        return self.__class__
    
    def set_incoming(self,object):
        self.info["incoming"] = object

    def set_running(self,object):
        self.info["running"] = object

    def get_source(self,closed_check = False):
        """Gets the 'source' for the transformer.
        This would either be an actual source type, a bus, or a transformer.
        Returns the source object.
        Optionally returns if all breakers on that path are closed."""
        source = None
        closed = True
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
            elif source.whoami() == Transformer:
                break
            else:
                source = source.info["incoming"]

        value = source

        if closed_check == True:
            value = closed

        return value

    def calculate(self):
        source = self.get_source()
        closed = self.get_source(True)

        if closed:
            self.info["voltage"] = source.info["voltage"]*self.info["factor"]
            self.info["frequency"] = source.info["frequency"]
            self.info["phase"] = source.info["phase"]
        else:
            self.info["voltage"] = 0
            self.info["frequency"] = 0
            self.info["phase"] = 0

        if self.info["running"].whoami() == Bus:
            if closed:
                self.info["running"].register_feeder(self)
                
                total_load = 0
                for load in self.info["running"].info["loads"]:
                    total_load += self.info["running"].info["loads"][load]

                self.info["current"] = total_load/(self.info["running"].info["voltage"]+0.1)
                resistance = 0.2
                dropped_voltage = self.info["current"]*resistance
                self.info["voltage"] = self.info["voltage"] - dropped_voltage



graph = None

def initialize():

    Source(name="ASHE500",voltage=500000,frequency=60) #Ashe 500kv line
    Source(name="ASHE230",voltage=230000,frequency=60) #Ashe 230kv line
    Source(name="BPA115",voltage=115000,frequency=60) #Benton 115kv line
    Source(name="DG1",voltage=0,frequency=0)
    Source(name="DG2",voltage=0,frequency=0)
    Source(name="DG3",voltage=0,frequency=0)
    Source(name="GEN",voltage=0,frequency=0)

    Source(name="ASDA",voltage=0,frequency=0)
    Source(name="ASDB",voltage=0,frequency=0)

    Bus(name="s_bus_4160",voltage=4160,frequency=60,rated_voltage=4160)
    Bus(name="s_bus_6900",voltage=6900,frequency=60,rated_voltage=6900)
    Bus(name="b_bus",voltage=4160,frequency=60,rated_voltage=4160)

    Transformer(name="tr_s",incoming=sources["ASHE230"],running=busses["s_bus_4160"],factor=0.01808695652,voltage=4160,frequency=60)
    Transformer(name="tr_s_6900",incoming=sources["ASHE230"],running=busses["s_bus_6900"],factor=0.03,voltage=6900,frequency=60)

    Breaker(name="cb_trb",running=busses["b_bus"],closed=True,custom=True) #Custom because i dont have a switch yet for it
    Transformer(name="tr_b",incoming=sources["BPA115"],running=breakers["cb_trb"],factor=0.03617391304)

    breakers["cb_trb"].set_incoming(transformers["tr_b"])

    Bus(name="gen_bus",voltage=0,frequency=0,rated_voltage=25000)
    Bus(name="main_bus",voltage=0,frequency=0,rated_voltage=500000)

    Bus(name="1",voltage=4160,frequency=60,rated_voltage=4160)
    Bus(name="2",voltage=4160,frequency=60,rated_voltage=4160)
    Bus(name="3",voltage=4160,frequency=60,rated_voltage=4160)

    Bus(name="11",voltage=480,frequency=60,rated_voltage=480)
    Bus(name="21",voltage=480,frequency=60,rated_voltage=480)
    Bus(name="31",voltage=480,frequency=60,rated_voltage=480)

    Bus(name="5",voltage=6900,frequency=60,rated_voltage=6900)
    Bus(name="6",voltage=6900,frequency=60,rated_voltage=6900)

    Bus(name="asda",voltage=0,frequency=0,rated_voltage=6900)
    Bus(name="asdb",voltage=0,frequency=0,rated_voltage=6900)

    Breaker(name="cb_rpt_4b",incoming=sources["ASDB"],closed=True)
    Breaker(name="cb_rpt_3b",incoming=breakers["cb_rpt_4b"],running=busses["asdb"],closed=True)

    breakers["cb_rpt_4b"].set_running(breakers["cb_rpt_3b"])

    Breaker(name="cb_rpt_4a",incoming=sources["ASDA"],closed=True)
    Breaker(name="cb_rpt_3a",incoming=breakers["cb_rpt_4a"],running=busses["asda"],closed=True)

    breakers["cb_rpt_4a"].set_running(breakers["cb_rpt_3a"])

    Bus(name="7",voltage=4160,frequency=60,rated_voltage=4160)
    Bus(name="4",voltage=4160,frequency=60,rated_voltage=4160)
    Bus(name="8",voltage=4160,frequency=60,rated_voltage=4160)
    
    Breaker(name="cb_s1",incoming=busses["s_bus_4160"],running=busses["1"],closed=True)
    Breaker(name="cb_s2",incoming=busses["s_bus_4160"],running=busses["2"],closed=True)
    Breaker(name="cb_s3",incoming=busses["s_bus_4160"],running=busses["3"],closed=True)

    Breaker(name="cb_s5",incoming=busses["s_bus_6900"],running=busses["5"],closed=True)
    Breaker(name="cb_s6",incoming=busses["s_bus_6900"],running=busses["6"],closed=True)

    Breaker(name="cb_1_7",incoming=busses["1"],closed=True)
    Breaker(name="cb_7_1",incoming=breakers["cb_1_7"],running=busses["7"],closed=True)

    breakers["cb_1_7"].set_running(breakers["cb_7_1"])

    #SL-11

    Breaker(name="cb_1_11",incoming=busses["1"],closed=True)
    Breaker(name="cb_11_1",running=busses["11"],closed=True)

    Transformer(name="tr_1_11",incoming=breakers["cb_1_11"],running=breakers["cb_11_1"],factor=0.1153846154)

    breakers["cb_1_11"].set_running(transformers["tr_1_11"])
    breakers["cb_11_1"].set_incoming(transformers["tr_1_11"])

    #SL-21

    Breaker(name="cb_2_21",incoming=busses["2"],closed=True)
    Breaker(name="cb_21_2",running=busses["21"],closed=True)

    Transformer(name="tr_2_21",incoming=breakers["cb_2_21"],running=breakers["cb_21_2"],factor=0.1153846154)

    breakers["cb_2_21"].set_running(transformers["tr_2_21"])
    breakers["cb_21_2"].set_incoming(transformers["tr_2_21"])

    Bus(name="2p",voltage=480,frequency=60,rated_voltage=480)


    Breaker(name="cb_21_2p",incoming=busses["21"],running=busses["2p"],closed=True,custom=True)

    #SL-31

    Breaker(name="cb_3_31",incoming=busses["3"],closed=True)
    Breaker(name="cb_31_3",running=busses["31"],closed=True)

    Transformer(name="tr_3_31",incoming=breakers["cb_3_31"],running=breakers["cb_31_3"],factor=0.1153846154)

    breakers["cb_3_31"].set_running(transformers["tr_3_31"])
    breakers["cb_31_3"].set_incoming(transformers["tr_3_31"])

    #SM-1 to 7

    Breaker(name="cb_1_7",incoming=busses["1"],closed=True)
    Breaker(name="cb_7_1",incoming=breakers["cb_1_7"],running=busses["7"],closed=True)

    breakers["cb_1_7"].set_running(breakers["cb_7_1"])

    #SM-2 to 4

    Breaker(name="cb_2_4",incoming=busses["2"],closed=True)
    Breaker(name="cb_4_2",incoming=breakers["cb_2_4"],running=busses["4"],closed=True)

    breakers["cb_2_4"].set_running(breakers["cb_4_2"])

    #SM-3 to 8

    Breaker(name="cb_3_8",incoming=busses["3"],closed=True)
    Breaker(name="cb_8_3",incoming=breakers["cb_3_8"],running=busses["8"],closed=True)

    breakers["cb_3_8"].set_running(breakers["cb_8_3"])

    #TR-B to SM-7

    Breaker(name="cb_b7",incoming=busses["b_bus"],running=busses["7"])

    #TR-B to SM-8

    Breaker(name="cb_b8",incoming=busses["b_bus"],running=busses["8"])

    #DG1

    Breaker(name="cb_dg1_7",incoming=sources["DG1"],custom=True) #has a mode selector
    Breaker(name="cb_7dg1",incoming=breakers["cb_dg1_7"],running=busses["7"],closed=True)

    breakers["cb_dg1_7"].set_running(breakers["cb_7dg1"])

    #DG2

    Breaker(name="cb_dg2_8",incoming=sources["DG2"],custom=True) #has a mode selector
    Breaker(name="cb_8dg2",incoming=breakers["cb_dg2_8"],running=busses["8"],closed=True)

    breakers["cb_dg2_8"].set_running(breakers["cb_8dg2"])

    #DG3

    Breaker(name="cb_dg3_4",incoming=sources["DG3"],running=busses["4"])

    #SM-7 loads

    Bus(name="73",voltage=480,frequency=60,rated_voltage=480)

    Breaker(name="cb_7_73",incoming=busses["7"],closed=True)

    Transformer(name="tr_7_73",incoming=breakers["cb_7_73"],running=busses["73"],factor=0.1153846154)

    breakers["cb_7_73"].set_running(transformers["tr_7_73"])

    Bus(name="7e",voltage=480,frequency=60,rated_voltage=480)


    Breaker(name="cb_73_7e",incoming=busses["73"],running=busses["7e"],closed=True,custom=True)

    Bus(name="7a",voltage=480,frequency=60,rated_voltage=480)


    Breaker(name="cb_73_7a",incoming=busses["73"],running=busses["7a"],closed=True,custom=True)

    #SM-8 loads

    Bus(name="83",voltage=480,frequency=60,rated_voltage=480)

    Breaker(name="cb_8_83",incoming=busses["8"],closed=True)

    Transformer(name="tr_8_83",incoming=breakers["cb_8_83"],running=busses["83"],factor=0.1153846154)

    breakers["cb_8_83"].set_running(transformers["tr_8_83"])

    Bus(name="8e",voltage=480,frequency=60,rated_voltage=480)


    Breaker(name="cb_83_8e",incoming=busses["83"],running=busses["8e"],closed=True,custom=True)

    Bus(name="8a",voltage=480,frequency=60,rated_voltage=480)


    Breaker(name="cb_83_8a",incoming=busses["83"],running=busses["8a"],closed=True,custom=True)

    #Main Generator

    Breaker(name="gen_output",incoming=sources["GEN"],running=busses["gen_bus"],closed=True,custom=True)

    Transformer(name="tr_m",incoming=busses["gen_bus"],running=busses["main_bus"],factor=20)

    Breaker(name="cb_4885",incoming=sources["ASHE500"],running=busses["main_bus"])

    Breaker(name="cb_4888",incoming=sources["ASHE500"],running=busses["main_bus"])


    
    global graph

    #graph = transient.Transient("SM-1/2/3 Response - Condensate Pump Starts while on the Startup Transformer")

    #graph.add_graph("SM-1 Voltage")
    #graph.add_graph("SM-2 Voltage")
    #graph.add_graph("SM-3 Voltage")

    #graph.add_graph("TR-S Current")

    #graph.add_graph("DG1 Voltage")
    #graph.add_graph("DG1 Field Voltage")
    #graph.add_graph("DG1 Frequency")

time7 = 0 #Temporary, move to its own py file
time8 = 0 #Temporary, move to its own py file

def run():

    global graph

    #TODO: Move elsewhere

    model.indicators["cr_light_normal_1"] = bool(busses["11"].is_voltage_at_bus(240)) #not DG-Backed
    model.indicators["cr_light_normal_2"] = bool(busses["31"].is_voltage_at_bus(240))
    model.indicators["cr_light_normal_3"] = busses["7e"].is_voltage_at_bus(240) #standby or "emergency/normal" lighting (half of the system)
    model.indicators["cr_light_normal_4"] = busses["8e"].is_voltage_at_bus(240)

    model.indicators["cr_light_normal_5"] = busses["7"].is_voltage_at_bus(3000) #standby or "emergency/normal" lighting (half of the system) (not load-shed)
    model.indicators["cr_light_normal_6"] = busses["8"].is_voltage_at_bus(3000)
    model.indicators["cr_light_emergency"] = not (busses["7"].is_voltage_at_bus(3000) and busses["8"].is_voltage_at_bus(3000)) #Emergency Egress Lighting
    
    #TODO: divisional emergency lights

    #graph.add("SM-1 Voltage",round(busses["1"].info["voltage"]))
    #graph.add("SM-2 Voltage",round(busses["2"].info["voltage"]))
    #graph.add("SM-3 Voltage",round(busses["3"].info["voltage"]))

    #graph.add("TR-S Current",round(transformers["tr_s"].info["current"]))

    #graph.add("DG1 Voltage",sources["DG1"].info["voltage"])
    #graph.add("DG1 Field Voltage",diesel_generator.dg1.dg["field_voltage"])
    #graph.add("DG1 Frequency",sources["DG1"].info["frequency"])

    #log.info(str(busses["7"].voltage_at_bus()))

    #if model.runs*0.1 > 30:
        #graph.generate_plot()

    for source in sources:
        source = sources[source]
        source.calculate()

    for transformer in transformers:
        transformer = transformers[transformer]
        transformer.calculate()

    for breaker in breakers:
        breaker = breakers[breaker]
        breaker.calculate()

    for bus in busses:
        bus = busses[bus]
        bus.calculate()

    #This loop is ONLY for logic!
    global time7
    global time8
    for bus in busses:
        bus = busses[bus]
        #Primary undervoltage 
        if bus.info["voltage"]/bus.info["rated_voltage"] < 0.69:
            #TODO: load shedding

            if bus.name == "4":
                diesel_generator.dg3.start(auto = True)

                if diesel_generator.dg3.dg["voltage"] >= 4160: #HPCS immediately transfers, right?
                    breakers["cb_dg3_4"].close()

                breakers["cb_4_2"].open()

            if bus.name == "7":
                diesel_generator.dg1.start(auto = True)

                time7 += 0.1

                if time7 > 5.5 and busses["b_bus"].is_voltage_at_bus(2000):
                    #Close the TRB breaker, if its available
                    breakers["cb_b7"].close()

                if diesel_generator.dg1.dg["voltage"] >= 4160 and time7 > 5.5 and not breakers["cb_b7"].info["closed"]:
                    breakers["cb_dg1_7"].close()

                breakers["cb_7_1"].open()

            if bus.name == "8":
                diesel_generator.dg2.start(auto = True)

                time8 += 0.1

                if time8 > 5.5 and busses["b_bus"].is_voltage_at_bus(2000):
                    #Close the TRB breaker, if its available
                    breakers["cb_b8"].close()

                if diesel_generator.dg2.dg["voltage"] >= 4160 and time8 > 5.5 and not breakers["cb_b8"].info["closed"]:
                    breakers["cb_dg2_8"].close()

                breakers["cb_8_3"].open()

        else:

            if bus.name == "7":
                time7 = 0

            if bus.name == "8":
                time8 = 0

    model.switches["cb_b8"]["lights"]["xfer"] = busses["b_bus"].is_voltage_at_bus(2000) #TODO: Move these
    model.switches["cb_b7"]["lights"]["xfer"] = busses["b_bus"].is_voltage_at_bus(2000)


    #TODO: Secondary undervoltage
