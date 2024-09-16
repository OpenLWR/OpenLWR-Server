from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.general_physics import fluid
from simulation.models.control_room_columbia.reactor_physics import pressure
import math


def clamp(val, clamp_min, clamp_max):
    return min(max(val,clamp_min),clamp_max)

def calculate_header_pressure(header_name:str):

    header = fluid.headers[header_name]

    from simulation.models.control_room_columbia.reactor_physics import pressure
    header_press = pressure.PartialPressure(pressure.GasTypes["Steam"],header["mass"],60,header["volume"])
    header["pressure"] = header_press

def run(delta):

    for valve_name in fluid.valves:
        valve = fluid.valves[valve_name]

        if valve["input"] == None or valve["output"] == None:
            continue

        inlet = fluid.get_header(valve["input"])
        if valve["output"] == "magic":
            outlet = {"pressure": 0,"mass" : 0,"type" : fluid.FluidTypes.Gas}
        else:
            outlet = fluid.get_header(valve["output"])

        if inlet["type"] == fluid.FluidTypes.Liquid or outlet["type"] == fluid.FluidTypes.Liquid:
            continue #this is handled by fluid.py

        #gas has to be calculated differently
        #It is the exact same as regular fluids, however it has an extra factor, (P1+P2/2*P2), expressing the average pressure relative to the outlet pressure

        radius = valve["diameter"]/2
        radius = radius*0.1 #to cm
        
        flow_resistance = (8*3.3*10000)/(math.pi*(radius**4))

        flow = (inlet["pressure"]-max(outlet["pressure"],0))/flow_resistance

        #here is our extra factor
        #if max(outlet["pressure"],0) != 0:
            #flow = (inlet["pressure"]+max(outlet["pressure"],0))/(2*(max(outlet["pressure"],0)))

        flow = abs(flow)

        flow = flow*(valve["percent_open"]/100)
        #flow is in cubic centimeters per second
        flow = flow/1000 #to liter/s
        
        flow = flow*delta #to liter/0.1s (or the sim time)
       
        if inlet["pressure"] < outlet["pressure"]:
            valve["flow"] = 0
            continue
        else:
            fluid.valve_inject_to_header(flow*-1,valve["input"])
            if valve["output"] != "magic":
                fluid.valve_inject_to_header(flow,valve["output"])

        valve["flow"] = flow

    print(fluid.headers["bypass_steam_header"]["pressure"]/6895)