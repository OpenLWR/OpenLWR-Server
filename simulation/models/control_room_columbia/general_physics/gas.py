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


        #Poiseuille's law
        #Q = π(P₁ – P₂)r⁴ / 8μL.
        #where,
        #Q is the volumetric flow rate,
        #P1 and P2 are the pressures at both ends of the pipe,
        #r is the radius of the pipe,
        #μ is the viscosity of the fluid,
        #L is the length of the pipe.

        #viscosity of steam (saturated steam at 1000 psia) = 0.00019 poise
        #placeholder 20000 mm as length (so 20 cm)

        radius = valve["diameter"]/2
        radius = radius*0.1 #to cm

        flow_resistance = (8*33*2000)/(math.pi*(radius**4))

        #flow = math.pi*((inlet["pressure"]*0.001)-(outlet["pressure"]*0.001))*(radius**4)/(8*0.01*200)

        flow = (inlet["pressure"]-outlet["pressure"])/flow_resistance
        flow = abs(flow)

        flow = flow*(valve["percent_open"]/100) #TODO: Exponents? Flow is not linear.
        #flow is in cubic centimeters per second
        flow = flow/1000 #to liter/s
        valve["flow"] = flow
        flow = flow*0.1 #to liter/0.1s (or the sim time)
        if inlet["pressure"] < outlet["pressure"]:
            #valve_inject_to_header(flow,valve["input"])
            #valve_inject_to_header(flow*-1,valve["output"])
            continue
        else:
            fluid.valve_inject_to_header(flow*-1,valve["input"])
            if valve["output"] != "magic":
                fluid.valve_inject_to_header(flow,valve["output"])
