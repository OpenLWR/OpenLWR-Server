from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.general_physics import fluid
from simulation.models.control_room_columbia.general_physics import ac_power

asda = {
    "demand" : 15,
    "actual" : 0,
    "auto" : False,
    "started" : False,
}

asdb = {
    "demand" : 15,
    "actual" : 0,
    "auto" : False,
    "started" : False,
}

def run():
    #Should we actually properly simulate the ASD?
    if ac_power.busses["6"].is_voltage_at_bus(4160) and asdb["started"]: #TODO: Bus voltage/frequency effect on ASD
        asdb["actual"] += min(asdb["demand"]-asdb["actual"],0.6)
    else:
        asdb["actual"] = 0
        asdb["started"] = False

    if ac_power.busses["5"].is_voltage_at_bus(4160) and asda["started"]: #TODO: Bus voltage/frequency effect on ASD
        asda["actual"] += min(asda["demand"]-asda["actual"],0.6)
    else:
        asda["actual"] = 0
        asda["started"] = False

    if model.buttons["rrc_b_start"]["state"]:
        asdb["started"] = True

    if model.buttons["rrc_a_start"]["state"]:
        asda["started"] = True

    if model.buttons["station_1b_lower"]["state"]:
        asdb["demand"] = max(15,asdb["demand"]-0.1)

    if model.buttons["station_1b_raise"]["state"]:
        asdb["demand"] = min(65,asdb["demand"]+0.1)

    if model.buttons["station_1a_lower"]["state"]:
        asda["demand"] = max(15,asda["demand"]-0.1)

    if model.buttons["station_1a_raise"]["state"]:
        asda["demand"] = min(65,asda["demand"]+0.1)



    model.values["rrc_p_1b_volts"] = ac_power.busses["asdb"].voltage_at_bus()
    model.values["rrc_p_1b_amps"] = model.pumps["rrc_p_1b"]["amperes"]
    model.values["rrc_p_1b_freq"] = asdb["actual"]
    model.values["rrc_p_1b_speed"] = model.pumps["rrc_p_1b"]["rpm"]

    model.values["station_1b_flow"] = model.pumps["rrc_p_1b"]["flow"]
    model.values["station_1b_bias"] = asdb["actual"]-asdb["demand"]
    model.values["station_1b_demand"] = asdb["demand"]
    model.values["station_1b_actual"] = asdb["actual"]

    ac_power.sources["ASDB"].info["frequency"] = asdb["actual"]
    ac_power.sources["ASDB"].info["voltage"] = ac_power.busses["6"].voltage_at_bus()#asdb["actual"]*115 #115 volts per hertz

    model.values["rrc_p_1a_volts"] = ac_power.busses["asda"].voltage_at_bus()
    model.values["rrc_p_1a_amps"] = model.pumps["rrc_p_1a"]["amperes"]
    model.values["rrc_p_1a_freq"] = asda["actual"]
    model.values["rrc_p_1a_speed"] = model.pumps["rrc_p_1a"]["rpm"]

    model.values["station_1a_flow"] = model.pumps["rrc_p_1a"]["flow"]
    model.values["station_1a_bias"] = asda["actual"]-asda["demand"]
    model.values["station_1a_demand"] = asda["demand"]
    model.values["station_1a_actual"] = asda["actual"]

    ac_power.sources["ASDA"].info["frequency"] = asda["actual"]
    ac_power.sources["ASDA"].info["voltage"] = ac_power.busses["5"].voltage_at_bus()#asda["actual"]*115 #115 volts per hertz