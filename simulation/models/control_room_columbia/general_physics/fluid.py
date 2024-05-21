from simulation.constants.electrical_types import ElectricalType
from simulation.constants.equipment_states import EquipmentStates
from simulation.models.control_room_columbia.general_physics import ac_power
from simulation.models.control_room_columbia import model
import math

def clamp(val, clamp_min, clamp_max):
    return min(max(val,clamp_min),clamp_max)


headers = { #most lines have a common header that they discharge into
    #this header can pressurize and etc.
    #takes a pipe diameter and length.
    "hpcs_discharge_header" : {
        #This next comment will be present on ALL headers.
        #it indicates the real pipe that this header was made from.
        #16" HPCS(1)-4-1

        "diameter" : 406.40, #millimeters
        "length" : 20000, #TODO : determine a good length
        "pressure" : 0, #pascals
        "volume" : 0, #Initialized on start. Is not changed again.
        "mass" : 0,
    }

}

#TODO: improve this shit

from enum import IntEnum

class StaticTanks(IntEnum):
    Reactor = 1
    Wetwell = 2,

valves = {
    "hpcs_v_4" : { #The flow through a valve is not linear. Exponents?
        "control_switch" : "hpcs_v_4",
        "input" : "hpcs_discharge_header",
        "output" : StaticTanks.Reactor,
        "percent_open" : 0,
        "diameter" : 406.40, #mm
        "open_speed" : 0.333, #30 seconds to open from full closed.
        "seal_in" : True, #Valve is seal-in, meaning it is not throttable (normally)
        "sealed_in" : False, #current state
        #TODO: valve control power and motive power
    }
}

def initialize_headers():

    for header_name in headers:
        header = headers[header_name]
        #assume the header is a cylinder
        #so we use pi*r^2
        volume = header["diameter"]/2
        volume = math.pi*(volume**2)
        #then multiply by the height
        volume = volume*header["length"]
        #this stuff is 8th grade math, i hope you know it
        volume = volume/1e6 #to liters
        header["volume"] = volume
        header["mass"] = 0

def valve_inject_to_header(mass:int,header_name):

    if type(header_name) == StaticTanks:
        inject_to_static_tank(header_name,mass)
    else:
        headers[header_name]["mass"] += mass
        calculate_header_pressure(header_name)


def inject_to_header(flow:int,press:int,header_name:str):

    #TODO: feedback to allow pump shutoff head
    header = headers[header_name]
    press = press*6895 # to pascals

    if press > header["pressure"]:
        fluid_flow = calculate_differential_pressure(press,header["pressure"],flow)
        #keep in mind this is in gallons per minute
        mass = fluid_flow*3.785 #to liters per minute
        mass = mass/60 #to per second
        mass = mass*0.1 # sim time
        header["mass"] += mass

        #TODO: change this, we are using the ideal gas law to calculate water, a *liquid* in a pipe.
        from simulation.models.control_room_columbia.reactor_physics import pressure
        header_press = pressure.PartialPressure(pressure.GasTypes["Steam"],24.8,60,header["volume"]-header["mass"])
        header["pressure"] = header_press
        return fluid_flow
    else:
        return 0

def calculate_header_pressure(header_name:str):

    header = headers[header_name]

    from simulation.models.control_room_columbia.reactor_physics import pressure
    header_press = pressure.PartialPressure(pressure.GasTypes["Steam"],24.8,60,header["volume"]-header["mass"])
    header["pressure"] = header_press

def calculate_differential_pressure(pressure_1:int,pressure_2:int,flow:int):

    """Calculates differential pressure vs flow in a system. Can use any units, as long as the pressures are both the same unit."""

    if pressure_2 == 0: pressure_2 = 1

    if pressure_1 > pressure_2:
        pressure_differential = clamp(abs(((pressure_1/pressure_2)-0.3)-1),0,1)
        fluid_flow = pressure_differential*flow

        return fluid_flow
    else:
        return 0

def get_static_tank(name:int):

    match name:
        case StaticTanks.Reactor:
            tank = {}
            from simulation.models.control_room_columbia.reactor_physics import pressure
            tank["pressure"] = pressure.Pressures["Vessel"]
            tank["mass"] = 0
            return tank

def inject_to_static_tank(name:int,amount):

    match name:
        case StaticTanks.Reactor:
            from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
            reactor_inventory.add_water(amount)
    

def get_header(header_name):
    "Can be passed an integer or string. If integer, it will check against the static tanks, and return a formatted table."

    header = {}

    if type(header_name) == StaticTanks:
        header = get_static_tank(header_name)
    else:
        header = headers[header_name]
    
    return header

def run():

    #TODO: figure out a better way to do this
    model.values["hpcs_flow"] = model.pumps["hpcs_p_1"]["actual_flow"]
    model.values["hpcs_press"] = headers["hpcs_discharge_header"]["pressure"]/6895

    for valve_name in valves:
        valve = valves[valve_name]
        inlet = get_header(valve["input"])
        outlet = get_header(valve["output"])

        if valve["control_switch"] != "":
            if not valve["seal_in"]:
                if model.switches[valve["control_switch"]]["position"] == 2:
                    valve["percent_open"] = min(max(valve["percent_open"]+valve["open_speed"],0),100)
                elif model.switches[valve["control_switch"]]["position"] == 0:
                    valve["percent_open"] = min(max(valve["percent_open"]-valve["open_speed"],0),100)
            elif valve["seal_in"]:
                if model.switches[valve["control_switch"]]["position"] == 2:
                    valve["sealed_in"] = True
                elif model.switches[valve["control_switch"]]["position"] == 0:
                    valve["sealed_in"] = False

                if valve["sealed_in"]:
                    valve["percent_open"] = min(max(valve["percent_open"]+valve["open_speed"],0),100)
                else:
                    valve["percent_open"] = min(max(valve["percent_open"]-valve["open_speed"],0),100)

            if model.switches[valve["control_switch"]]["lights"] != {}:
                model.switches[valve["control_switch"]]["lights"]["green"] = valve["percent_open"] < 100
                model.switches[valve["control_switch"]]["lights"]["red"] = valve["percent_open"] > 0
      



        #Poiseuille's law
        #Q = π(P₁ – P₂)r⁴ / 8μL.
        #where,
        #Q is the volumetric flow rate,
        #P1 and P2 are the pressures at both ends of the pipe,
        #r is the radius of the pipe,
        #μ is the viscosity of the fluid,
        #L is the length of the pipe.

        #viscosity of water is 0.01 poise
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
        flow = flow*0.1 #to liter/0.1s (or the sim time)
        if inlet["pressure"] < outlet["pressure"]:
            #valve_inject_to_header(flow,valve["input"])
            #valve_inject_to_header(flow*-1,valve["output"])
            continue
        else:
            valve_inject_to_header(flow*-1,valve["input"])
            valve_inject_to_header(flow,valve["output"])
