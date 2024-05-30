from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.general_physics import fluid
from simulation.models.control_room_columbia.general_physics import gas
import math

def clamp(val, clamp_min, clamp_max):
    return min(max(val,clamp_min),clamp_max)

turbine_template = {
    "rpm" : 0,
    "rated_rpm" : 6250,
    "flow_to_rpm" : 0,
    "acceleration_value" : 0,
    "trip" : False,
    "mechanical_trip" : False,
    "trip_valve" : "",
    "steam_flow_valve" : "",
    "governor_valve" : "",
}

def initialize_pumps():
    for turbine_name in model.turbines:
        turbine = model.turbines[turbine_name]
        import copy
        turbine_created = copy.deepcopy(turbine_template)

        for value_name in turbine:
            value = turbine[value_name]
            if value_name in turbine_created:
                turbine_created[value_name] = value

        model.turbines[turbine_name] = turbine_created

def run():
    for turbine_name in model.turbines:
        turbine = model.turbines[turbine_name]

        #TODO: Better simulation
        #TODO: Un-hardcode this

        if turbine["trip"] or turbine["mechanical_trip"]:
            fluid.valves[turbine["trip_valve"]]["sealed_in"] = False

        steam_flow_permitted = fluid.headers["rcic_turbine_steam_line"]

        radius = 100/2
        radius = radius*0.1 #to cm

        flow_resistance = (8*33*2000)/(math.pi*(radius**4))


        flow = (steam_flow_permitted["pressure"]-0)/flow_resistance
        flow = abs(flow)

        flow *= (fluid.valves[turbine["trip_valve"]]["percent_open"]/100)
        #steam_flow_permitted *= (fluid.valves[turbine["steam_flow_valve"]]["percent_open"]/100)
        #steam_flow_permitted *= (fluid.valves[turbine["governor_valve"]]["percent_open"]/100)

        acceleration = ((flow/turbine["flow_to_rpm"])-turbine["rpm"])*turbine["acceleration_value"]

        #flow is in cubic centimeters per second
        flow = flow/1000 #to liter/s
        flow = flow*0.1 #to liter/0.1s (or the sim time)\

        steam_flow_permitted["mass"] -= flow
        fluid.headers["rcic_exhaust_steam_line"]["mass"] += flow

        gas.calculate_header_pressure("rcic_turbine_steam_line")
        gas.calculate_header_pressure("rcic_exhaust_steam_line")

        turbine["rpm"] += acceleration










        
    
    


