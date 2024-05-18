from simulation.constants.electrical_types import ElectricalType
import math

def clamp(val, clamp_min, clamp_max):
    return min(max(val,clamp_min),clamp_max)

breakers = {
	
}

busses = {
     
}

transformers = {
	
}

sources = {
    "Startup" : { #make this an actual transformer later
        "type" : ElectricalType.SOURCE,
        "voltage" : 4160,
        "frequency" : 60,

        "annunciators" : {}
    }
}

def run(switches,alarms,indicators,runs):

    indicators["cr_light_normal"] = True#get_bus_power("101",4000)
    indicators["cr_light_emergency"] = False#not get_bus_power("101",4000)
    for breaker_name in breakers:
        if breaker_name in switches:
            if switches[breaker_name]["position"] == 0: open_breaker(breaker_name)

            if switches[breaker_name]["position"] == 2: close_breaker(breaker_name)

        indicators[breaker_name+"_green"] = not breakers[breaker_name]["closed"]

        indicators[breaker_name+"_red"] = breakers[breaker_name]["closed"]

        #TODO: find a way to resolve this minor pyramid
        if breakers[breaker_name]["closed"]:
            if get_type(breakers[breaker_name]["running"]) == ElectricalType.BUS:
                #add this breaker to that busses feeders, if it isnt already there
                #TODO: clean this up
                if not breaker_name in busses[breakers[breaker_name]["running"]]["feeders"]:
                    busses[breakers[breaker_name]["running"]]["feeders"].append(breaker_name)
                 

    for bus_name in busses:
        bus = busses[bus_name]
		#handling for breaker interactions with the bus
        for feeder in bus["feeders"]:
            #remove the feeder if its not supplying anything
            match get_type(feeder):
                case ElectricalType.BREAKER:
                    component = breakers[feeder]
                    if not verify_path_closed(feeder):
                        bus["feeders"].remove(feeder)
            
                    #TODO: interactions between multiple feeders

                    source = trace_source(component)

                    bus["voltage"] = source["voltage"]
                    bus["frequency"] = source["frequency"]
                case ElectricalType.TRANSFORMER:
                    component = transformers[feeder]
                    if not component["breakers_closed"]:
                        bus["feeders"].remove(feeder)
                    
                    source = component

                    bus["voltage"] = source["voltage"]
                    bus["frequency"] = source["frequency"]
           

        if len(bus["feeders"]) == 0:
            bus["voltage"] = 0
            bus["frequency"] = 0
        
        if bus["voltage"] < bus["undervoltage_setpoint"]:
            if "UNDERVOLTAGE" in bus["annunciators"]:
                alarms[bus["annunciators"]["UNDERVOLTAGE"]]["alarm"] = True

    for transformer_name in transformers:
        xfmr = transformers[transformer_name]
        input_source = trace_source(xfmr["incoming"])
        #TODO: remove this hardcoded stuff
        incoming_voltage = 0
        incoming_frequency = 0
        if get_type(xfmr["incoming"]) == ElectricalType.BREAKER:
            input_breaker = type_check(get_type(xfmr["incoming"]))[xfmr["incoming"]]
            xfmr["breakers_closed"] = input_breaker["closed"]
            if input_breaker["closed"]:
                incoming_voltage = input_source["voltage"]
                incoming_frequency = input_source["frequency"]
                if get_type(xfmr["running"]) == ElectricalType.BUS:
                    busses[xfmr["running"]]["feeders"].append(transformer_name)

        xfmr["voltage"] = incoming_voltage
        xfmr["frequency"] = incoming_frequency

    #from general_physics import diesel_generator
    #diesel_generator.run()



def trace_source(incoming):
    '''Traces the source that is currently supplying voltage. Can be a bus or source.'''
    source = ""
    if type(incoming) == str: incoming = type_check(get_type(incoming))[incoming]

    if incoming["type"] == ElectricalType.BUS: return incoming #if the given trace is already a bus, just return that

    while True:
        if source == "":
            source = incoming["incoming"]

        if get_type(source) == ElectricalType.BUS:
            source = busses[source]
            break
        elif get_type(source) == ElectricalType.SOURCE:
            source = sources[source]
            break
        else:
            #this is a bit messy
            source = type_check(get_type(source))[source]["incoming"]

    return source

def verify_path_closed(incoming):
    '''Traces the source that is currently supplying voltage and verifys all breakers are closed. Returns true if all are closed.'''
    source = ""
    if type(incoming) == str: incoming = type_check(get_type(incoming))[incoming]

    if incoming["type"] == ElectricalType.BUS: return True #if the given trace is already a bus, just return true
    available = True
    while True:
        if source == "":
            if incoming["type"] == ElectricalType.BREAKER:
                if not incoming["closed"]: 
                    available = False
                    break
            source = incoming["incoming"]

        if get_type(source) == ElectricalType.BUS:
            break
        elif get_type(source) == ElectricalType.SOURCE:
            break
        elif get_type(source) == ElectricalType.BREAKER:
            if not type_check(get_type(source))[source]["closed"]: 
                available = False
                break

        source = type_check(get_type(source))[source]["incoming"]

    return available
        

def get_type(name):
    #TODO: find a better way to do this
    #NOTE: replace with a for loop?
    if "cb" in name:
        return ElectricalType.BREAKER
    if "tr" in name:
        return ElectricalType.TRANSFORMER
    if "Startup" in name:
        return ElectricalType.SOURCE
    else:
        return ElectricalType.BUS
        

def type_check(component_type:int):
    '''Checks the type of the component given. Returns the table that the type is in.'''
    if component_type > len(ElectricalType) or component_type < 0: print(f"Invalid type : {component_type}")

    match component_type: #TODO: is there a better way to do this?
        case ElectricalType.BREAKER: return breakers
        case ElectricalType.TRANSFORMER: return transformers
        case ElectricalType.BUS: return busses
        case ElectricalType.SOURCE: return sources

    print("Could not match given type with any defined type : "+str(type))
    return 
		
def open_breaker(breaker):
    component = breakers[breaker]
    #TODO: breakers failing to trip
    component["closed"] = False
	
def close_breaker(breaker):
    component = breakers[breaker]
    #TODO: breakers failing to close
    component["closed"] = True and not component["lockout"]
	
def set_lockout(component_type:int,name:str,state:bool):
    type_table = type_check(component_type)
    component = type_table[name]
    component["lockout"] = state

def get_bus_power(bus_name:str,undervoltage_setpoint:int):
    """Gets if the bus is powered, according to a undervoltage setpoint.

    Returns true if powered, else false."""
    if busses[bus_name]["voltage"] < undervoltage_setpoint: return False
    return True

#physics related functions

def VoltAmperesAC(voltage:int,amps:int,pf:float):
    """Gets the watts currently passing through an AC system.
    This will get the watts for a single phase system. Use TF_VoltAmperesAC for three phase.
    Voltage - Voltage, in volts.
    Amps - Amperes, in amps. (duh)
    pf - Power factor
    
    Returns the power, in watts."""

    watts = voltage*amps*pf

    return watts

def TF_VoltAmperesAC(voltage:int,amps:int,pf:float):
    """Gets the watts currently passing through an AC system.
    This will get the watts for a three phase system. Use VoltAmperesAC for single phase.
    Voltage - Voltage, in volts.
    Amps - Current, in amps. (duh)
    pf - Power factor
    
    Returns the power, in watts."""

    watts = voltage*amps*pf*math.sqrt(3)

    return watts