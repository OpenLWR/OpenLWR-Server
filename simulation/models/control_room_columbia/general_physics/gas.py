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

def run():

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
        #here i am attempting to usea combination of equations,
        #Reynolds Number, (Re=puL/μ)
        #Bernoulli's Equation, (P+1/2pv^2+pgh=constant)

        #Q=Cd*pi/4*d^2*[2(p1-p2)/p(1-d^4)]^1/2
        #this hurts my brain
        #Q = flow
        #Cd = Discharge Coefficient
        #p = Density of fluid
        #d = Diameter two/ Diameter one

        flow = 0
       
        if inlet["pressure"] < outlet["pressure"]:
            continue
        else:
            fluid.valve_inject_to_header(flow*-1,valve["input"])
            if valve["output"] != "magic":
                fluid.valve_inject_to_header(flow,valve["output"])
