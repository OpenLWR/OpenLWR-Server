from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.general_physics import fluid

rhr_a_lpcs_init = False
rhr_a_lpcs_init_first = False

rhr_cb_init = False
rhr_cb_init_first = False

def run():

    global rhr_a_lpcs_init
    global rhr_a_lpcs_init_first

    global rhr_cb_init
    global rhr_cb_init_first

    model.values["rhr_a_flow"] = model.pumps["rhr_p_2a"]["actual_flow"]
    model.values["rhr_a_press"] = fluid.headers["rhr_a_discharge_header"]["pressure"]/6895

    model.values["rhr_b_flow"] = model.pumps["rhr_p_2b"]["actual_flow"]
    model.values["rhr_b_press"] = fluid.headers["rhr_b_discharge_header"]["pressure"]/6895

    model.values["rhr_c_flow"] = model.pumps["rhr_p_2c"]["actual_flow"]
    model.values["rhr_c_press"] = fluid.headers["rhr_c_discharge_header"]["pressure"]/6895    

    if model.pumps["rhr_p_2a"]["motor_breaker_closed"]:
        fluid.valves["rhr_v_64a"]["sealed_in"] = model.pumps["rhr_p_2a"]["actual_flow"] < 1200

    if model.buttons["rhr_cb_init"]["state"]:
        rhr_cb_init = True
        rhr_cb_init_first = True

    if rhr_cb_init:
        if rhr_cb_init_first:
            model.pumps["rhr_p_2c"]["motor_breaker_closed"] = True
        
        fluid.valves["rhr_v_42c"]["sealed_in"] = True

    model.indicators["rhr_cb_init"] = rhr_cb_init