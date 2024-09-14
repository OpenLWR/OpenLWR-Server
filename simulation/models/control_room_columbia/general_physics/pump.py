from simulation.constants.electrical_types import ElectricalType
from simulation.constants.equipment_states import EquipmentStates
from simulation.models.control_room_columbia.general_physics import ac_power
from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.general_physics import fluid
import math
import log

def clamp(val, clamp_min, clamp_max):
    return min(max(val,clamp_min),clamp_max)

from enum import IntEnum

class PumpTypes(IntEnum):
    Type1 = 0
    Type2 = 1


pump_1 = { #TODO: improve the accuracy of these calculations
    #this pump is motor driven
    "motor_breaker_closed" : False,
    "was_closed" : False,
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
    "custom" : False,
    "shaft_driven" : False,

    "loop_seq" : False, # Has a LOOP Sequence (otherwise trips instantly)
    "loop_avail" : False, # Loop Sequence has permitted loading of this equipment, if needed
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

def calculate_suction(pump,delta):
    pump = model.pumps[pump]

    if pump["suct_header"] == "":
        return pump["flow"]
    
    suct_header = fluid.headers[pump["suct_header"]]
    disch_header = fluid.headers[pump["header"]]

    radius = suct_header["diameter"]/2
    radius = radius*0.1 #to cm

    flow_resistance = (8*33*20000)/(math.pi*(radius**4))

    flow = (suct_header["pressure"])/flow_resistance

    flow = max(flow,0)

    flow = flow/1000 #to liter/s

    flow = flow*15.850323140625 #to gpm

    flow = min(flow,pump["flow"])
        
    return flow
def run(delta):
    for pump_name in model.pumps:
        pump = model.pumps[pump_name]

        if pump["type"] == PumpTypes.Type2:
            pump_turbine = model.turbines[pump["turbine"]]
            pump["rpm"] = pump_turbine["rpm"]

            pump["flow"] = pump["rated_flow"]*(pump["rpm"]/pump["rated_rpm"])
            pump["flow"] = calculate_suction(pump_name,delta)
            pump["discharge_pressure"] = pump["rated_discharge_press"]*(pump["rpm"]/pump["rated_rpm"])
            
            pump["actual_flow"] = fluid.inject_to_header(pump["flow"],pump["discharge_pressure"],pump["header"])
            continue

        if pump["motor_control_switch"] != "":
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

        #undervoltage breaker trip TODO: (this has load sequencing during a LOOP? verify this)

        voltage = 0
        try:
            pump_bus = ac_power.busses[pump["bus"]]

            voltage = pump_bus.voltage_at_bus()

            if voltage < 120 and pump["motor_breaker_closed"] and not pump["custom"]:
                pump["motor_breaker_closed"] = False
                pump["was_closed"] = True
                continue

            if not pump_name in pump_bus.info["loads"]:
                pump_bus.register_load(pump["watts"],pump_name)
            else:
                pump_bus.modify_load(pump["watts"],pump_name)
        except:
            #log.warning("Pump does not have an available bus!")
            voltage = 4160


        if not pump["custom"]:
            if pump["loop_avail"] and pump["was_closed"]:
                pump["motor_breaker_closed"] = True
                pump["was_closed"] = False

        if pump["shaft_driven"]:
            pump["flow"] = pump["rated_flow"]*(pump["rpm"]/pump["rated_rpm"])
            pump["flow"] = calculate_suction(pump_name,delta)
            pump["discharge_pressure"] = pump["rated_discharge_press"]*(pump["rpm"]/pump["rated_rpm"])
            
            if pump["header"] != "":
                pump["actual_flow"] = fluid.inject_to_header(pump["flow"],pump["discharge_pressure"],pump["header"])
                if pump["suct_header"] != "":
                    fluid.headers[pump["suct_header"]]["mass"] -= pump["actual_flow"]
                    fluid.headers[pump["suct_header"]]["mass"] = max(fluid.headers[pump["suct_header"]]["mass"],0)
                    fluid.calculate_header_pressure(pump["suct_header"])
            else:
                pump["actual_flow"] = pump["flow"]

            continue

        if pump["motor_breaker_closed"]:
            #first, verify that this breaker is allowed to be closed

            #TODO: overcurrent breaker trip

            

            Acceleration = ((pump["rated_rpm"]*(pump_bus.info["frequency"]/60))-pump["rpm"])*1*delta #TODO: Make acceleration and frequency realistic
            pump["rpm"] = clamp(pump["rpm"]+Acceleration,0,pump["rated_rpm"]+100)
            #full load amperes
            if voltage > 0:
                AmpsFLA = (pump["horsepower"]*746)/((math.sqrt(3)*voltage*0.876*0.95)) #TODO: variable motor efficiency and power factor
            else:
                AmpsFLA = 0
            pump["amperes"] = (AmpsFLA*clamp(pump["actual_flow"]/pump["rated_flow"],0.48,1))+(AmpsFLA*5*(Acceleration/(pump["rated_rpm"]*1*delta)))
            pump["watts"] = voltage*pump["amperes"]*math.sqrt(3)

			#remember to make the loading process for the current (v.FLA*math.clamp(v.flow_with_fullsim etc)) more realistic, and instead make it based on distance from rated rpm (as when the pump is loaded more it will draw more current)
            #TODO: better flow calculation
            pump["flow"] = pump["rated_flow"]*(pump["rpm"]/pump["rated_rpm"])
            pump["flow"] = calculate_suction(pump_name,delta)
            pump["discharge_pressure"] = pump["rated_discharge_press"]*(pump["rpm"]/pump["rated_rpm"])
            
            if pump["header"] != "":
                pump["actual_flow"] = fluid.inject_to_header(pump["flow"],pump["discharge_pressure"],pump["header"])
                if pump["suct_header"] != "":
                    fluid.headers[pump["suct_header"]]["mass"] -= pump["actual_flow"]
                    fluid.headers[pump["suct_header"]]["mass"] = max(fluid.headers[pump["suct_header"]]["mass"],1)
                    fluid.calculate_header_pressure(pump["suct_header"])
            else:
                pump["actual_flow"] = pump["flow"]
        else:
            Acceleration = (pump["rpm"])*1*delta #TODO: variable motor accel
            pump["rpm"] = clamp(pump["rpm"]-Acceleration,0,pump["rated_rpm"]+100)
            pump["amperes"] = 0
            pump["watts"] = 0

            pump["flow"] = pump["rated_flow"]*(pump["rpm"]/pump["rated_rpm"])
            pump["flow"] = calculate_suction(pump_name,delta)
            pump["discharge_pressure"] = pump["rated_discharge_press"]*(pump["rpm"]/pump["rated_rpm"])

            if pump["header"] != "":
                pump["actual_flow"] = fluid.inject_to_header(pump["flow"],pump["discharge_pressure"],pump["header"])
                if pump["suct_header"] != "":
                    fluid.headers[pump["suct_header"]]["mass"] -= pump["actual_flow"]
                    fluid.headers[pump["suct_header"]]["mass"] = max(fluid.headers[pump["suct_header"]]["mass"],1)
                    fluid.calculate_header_pressure(pump["suct_header"])
            else:
                pump["actual_flow"] = pump["flow"]
    


