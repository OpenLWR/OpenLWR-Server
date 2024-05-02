from simulation.constants.electrical_types import ElectricalType

def clamp(val, clamp_min, clamp_max):
    return min(max(val,clamp_min),clamp_max)

breakers = {
	"cb_test_test2" : {
        "type" : ElectricalType.BREAKER,
		"closed" : True,
		"incoming" : "test", #"incoming" can be anything, and is generally the normal flow into the breaker
		#the breaker can flow in reverse, but this will take a bit more calculations than usual
        #TODO: breaker reverse current protection
		"running" : "test2", #"running" can be anything as well, and is generally the outgoing flow
		"lockout" : False, #most breakers have a lockout circuit which can trip automatically to prevent closure
		"flag_position" : False, #TODO: do we need this, or will this be included with the switch code?
    },
}

transformers = {
	
}

busses = {
     "test" : {
        "type" : ElectricalType.BUS,
        "voltage" : 480,
        "frequency" : 60,
        "current" : 0,
        "loads" : [],
        "feeders" : [],

        "undervoltage_setpoint" : 400,

        "annunciators" : {
             "UNDERVOLTAGE" : "bus_test_undervoltage",
        }
    },
    "test2" : {
        "type" : ElectricalType.BUS,
        "voltage" : 0,
        "frequency" : 0,
        "current" : 0,
        "loads" : [],
        "feeders" : [],

        "undervoltage_setpoint" : 400,

        "annunciators" : {
             "UNDERVOLTAGE" : "bus2_test_undervoltage",
        }
    },
}

sources = {}

def run(switches,alarms,indicators):
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
            component = breakers[feeder]
            #TODO: check what type the feeder is (IE Transformer v Breaker) and take action based on that
            if not component["closed"]:
                bus["feeders"].remove(feeder)
            
            #TODO: interactions between multiple feeders

            source = trace_source(component)

            bus["voltage"] = source["voltage"]
            bus["frequency"] = source["frequency"]

        if len(bus["feeders"]) == 0 and bus_name != "test":
            bus["voltage"] = 0
            bus["frequency"] = 0
        
        if bus["voltage"] < bus["undervoltage_setpoint"]:
            if "UNDERVOLTAGE" in bus["annunciators"]:
                alarms[bus["annunciators"]["UNDERVOLTAGE"]]["alarm"] = True


def trace_source(breaker:dict):
    source = ""
    while True:
        if source == "":
            source = breaker["incoming"]

        if get_type(source) == ElectricalType.BUS:
            break
        else:
            #this is a bit messy
            source = type_check(get_type(source))[source]["incoming"]

    return busses[source]
        

def get_type(name):
    #TODO: find a better way to do this
    #NOTE: replace with a for loop?
    if "cb" in name:
        return ElectricalType.BREAKER
    if "tr" in name:
        return ElectricalType.TRANSFORMER
    else:
        return ElectricalType.BUS
        

def type_check(component_type:int):
	
    if type > len(ElectricalType) or type < 0: print(f"Invalid type : {component_type}")

    match type: #TODO: is there a better way to do this?
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