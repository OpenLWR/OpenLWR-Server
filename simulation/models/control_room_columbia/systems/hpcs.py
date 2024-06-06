from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.general_physics import fluid

hpcs_init = False
hpcs_init_first = False


def run():

    global hpcs_init
    global hpcs_init_first

    model.values["hpcs_flow"] = model.pumps["hpcs_p_1"]["actual_flow"]
    model.values["hpcs_press"] = fluid.headers["hpcs_discharge_header"]["pressure"]/6895

    model.alarms["hpcs_init_rpv_level_low"]["alarm"] = hpcs_init

    if reactor_inventory.rx_level_wr < -51:
        hpcs_init = True

    if model.pumps["hpcs_p_1"]["motor_breaker_closed"]:
        fluid.valves["hpcs_v_12"]["sealed_in"] = model.pumps["hpcs_p_1"]["actual_flow"] < 1200

    if model.buttons["hpcs_init"]["state"]:
        hpcs_init = True
        hpcs_init_first = True

    if hpcs_init:
        if hpcs_init_first:
            model.pumps["hpcs_p_1"]["motor_breaker_closed"] = True
        
        fluid.valves["hpcs_v_4"]["sealed_in"] = True

    model.indicators["hpcs_init"] = hpcs_init