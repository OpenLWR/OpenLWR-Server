from simulation.constants.electrical_types import ElectricalType
from simulation.constants.equipment_states import EquipmentStates
from simulation.models.control_room_columbia.general_physics import ac_power
from simulation.models.control_room_columbia import model
import math

def clamp(val, clamp_min, clamp_max):
    return min(max(val,clamp_min),clamp_max)

from enum import IntEnum

class PumpTypes(IntEnum):
    Type1 = 0
    Type2 = 1


pump_1 = { #TODO: improve the accuracy of these calculations
    #this pump is motor driven
    "motor_breaker_closed" : False,
    "motor_control_switch" : "",
    "bus" : "",
    "horsepower" : 0,
    "watts" : 0,
    "amperes" : 0,
    "rpm" : 0,
    "discharge_press" : 0,
    "flow" : 0,
    "actual_flow" : 0,
    "rated_rpm" : 0,
    "rated_discharge_press" : 0,
    "flow_from_rpm" : 0,
    "rated_flow" : 0,
    "current_limit" : 0,
    "header" : "",
    "suct_header" : "",
    "type" : PumpTypes.Type1,
}

pump_2 = { #TODO: improve the accuracy of these calculations
    #this pump is shaft driven (turbine)
    "turbine" : "",
    "discharge_press" : 0,
    "flow" : 0,
    "actual_flow" : 0,
    "rated_rpm" : 0,
    "rated_discharge_press" : 0,
    "rated_flow" : 0,
    "header" : "",
    "suct_header" : "",
    "type" : PumpTypes.Type2,
}

def initialize_pumps():
    for pump_name in model.pumps:
        pump = model.pumps[pump_name]
        import copy
        #TODO: find a better way to do this
        if pump["type"] == PumpTypes.Type1:
            pump_created = copy.deepcopy(pump_1)
        else:
            pump_created = copy.deepcopy(pump_2)

        for value_name in pump:
            value = pump[value_name]
            if value_name in pump_created:
                pump_created[value_name] = value

        model.pumps[pump_name] = pump_created

def calculate_suction(pump):
    pump = model.pumps[pump]
    from simulation.models.control_room_columbia.general_physics import fluid
    suct_header = fluid.headers[pump["suct_header"]]
    disch_header = fluid.headers[pump["header"]]

    radius = suct_header["diameter"]/2
    radius = radius*0.1 #to cm

    flow_resistance = (8*33*2000)/(math.pi*(radius**4))

    flow = (suct_header["pressure"])/flow_resistance

    flow = max(flow,0)

    flow = flow/1000 #to liter/s

    flow_suct = flow*0.1 #to liter/0.1s (or the sim time)

    flow_suct = min(flow_suct,pump["flow"])
    #if suct_header["mass"] - flow_suct <= 0:
        #suct_header["mass"] = 0
        #return 0

    suct_header["mass"] -= flow_suct
    return (flow/3.785)*60

def run():
    for pump_name in model.pumps:
        pump = model.pumps[pump_name]

        if pump["type"] == PumpTypes.Type2:
            pump_turbine = model.turbines[pump["turbine"]]
            pump["rpm"] = pump_turbine["rpm"]

            pump["flow"] = pump["rated_flow"]*(pump["rpm"]/pump["rated_rpm"])
            pump["flow"] = calculate_suction(pump_name)
            pump["discharge_pressure"] = pump["rated_discharge_press"]*(pump["rpm"]/pump["rated_rpm"])
            
            from simulation.models.control_room_columbia.general_physics import fluid
            pump["actual_flow"] = fluid.inject_to_header(pump["flow"],pump["discharge_pressure"],pump["header"])
            continue

        
        if len(model.switches[pump["motor_control_switch"]]["positions"]) > 2:
            if model.switches[pump["motor_control_switch"]]["position"] == 2:
                pump["motor_breaker_closed"] = True
        else:
            if model.switches[pump["motor_control_switch"]]["position"] == 1:
                pump["motor_breaker_closed"] = True
        
        if model.switches[pump["motor_control_switch"]]["position"] == 0:
            pump["motor_breaker_closed"] = False

        if model.switches[pump["motor_control_switch"]]["lights"] != {}:
            model.switches[pump["motor_control_switch"]]["lights"]["green"] = not pump["motor_breaker_closed"]
            model.switches[pump["motor_control_switch"]]["lights"]["red"] = pump["motor_breaker_closed"]

        if pump["motor_breaker_closed"]:
            #first, verify that this breaker is allowed to be closed

            #TODO: overcurrent breaker trip

            #undervoltage breaker trip TODO: (this has load sequencing during a LOOP? verify this)
            try:
                pump_bus = ac_power.busses[pump["bus"]]
            except:
                pump_bus = {"voltage" : 4160}

            if pump_bus["voltage"] < 120:
                pump["motor_breaker_closed"] = False
                continue

            Acceleration = (pump["rated_rpm"]-pump["rpm"])*0.1 #TODO: variable motor accel
            pump["rpm"] = clamp(pump["rpm"]+Acceleration,0,pump["rated_rpm"]+100)
            #full load amperes
            AmpsFLA = (pump["horsepower"]*746)/(math.sqrt(3)*pump_bus["voltage"]*0.876*0.95) #TODO: variable motor efficiency and power factor
            pump["amperes"] = (AmpsFLA*clamp(pump["actual_flow"]/pump["rated_flow"],0.48,1))+(AmpsFLA*5*(Acceleration/(pump["rated_rpm"]*0.1)))
            pump["watts"] = pump_bus["voltage"]*pump["amperes"]*math.sqrt(3)

			#remember to make the loading process for the current (v.FLA*math.clamp(v.flow_with_fullsim etc)) more realistic, and instead make it based on distance from rated rpm (as when the pump is loaded more it will draw more current)
            #TODO: better flow calculation
            pump["flow"] = pump["rated_flow"]*(pump["rpm"]/pump["rated_rpm"])
            pump["flow"] = calculate_suction(pump_name)
            pump["discharge_pressure"] = pump["rated_discharge_press"]*(pump["rpm"]/pump["rated_rpm"])
            
            from simulation.models.control_room_columbia.general_physics import fluid
            pump["actual_flow"] = fluid.inject_to_header(pump["flow"],pump["discharge_pressure"],pump["header"])
        else:
            Acceleration = (pump["rpm"])*0.1 #TODO: variable motor accel
            pump["rpm"] = clamp(pump["rpm"]-Acceleration,0,pump["rated_rpm"]+100)
            pump["amperes"] = 0
            pump["watts"] = 0

            pump["flow"] = pump["rated_flow"]*(pump["rpm"]/pump["rated_rpm"])
            pump["flow"] = calculate_suction(pump_name)
            pump["discharge_pressure"] = pump["rated_discharge_press"]*(pump["rpm"]/pump["rated_rpm"])

            from simulation.models.control_room_columbia.general_physics import fluid
            pump["actual_flow"] = fluid.inject_to_header(pump["flow"],pump["discharge_pressure"],pump["header"])
    


