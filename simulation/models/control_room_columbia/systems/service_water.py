from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.general_physics import fluid

def run():
    if fluid.headers["sw_p_1a_discharge"]["pressure"]/6895 > 50:
        fluid.valves["sw_v_2a"]["sealed_in"] = True

    model.values["sw_a_flow"] = fluid.valves["rhr_v_68a"]["flow"]*15.85032
    model.values["sw_a_press"] = fluid.headers["sw_a_return"]["pressure"]/6895
    model.values["sw_p_1a_amps"] = model.pumps["sw_p_1a"]["amperes"]
    model.values["sw_a_temp"] = (fluid.SWPondATemp*1.8) + 32
    #print(fluid.SWPondATemp, model.reactor_water_temperature)
