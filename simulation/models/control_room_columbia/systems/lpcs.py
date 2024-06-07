from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.general_physics import fluid

def run():

    model.values["lpcs_flow"] = model.pumps["lpcs_p_1"]["actual_flow"]
    model.values["lpcs_press"] = fluid.headers["lpcs_discharge_header"]["pressure"]/6895

    #model.alarms["hpcs_init_rpv_level_low"]["alarm"] = hpcs_init

    if model.pumps["lpcs_p_1"]["motor_breaker_closed"]:
        fluid.valves["lpcs_v_11"]["sealed_in"] = model.pumps["lpcs_p_1"]["actual_flow"] < 1200

    #if model.buttons["hpcs_init"]["state"]:
        #hpcs_init = True
        #hpcs_init_first = True

    #if hpcs_init:
        #if hpcs_init_first:
            #model.pumps["hpcs_p_1"]["motor_breaker_closed"] = True
        
        #fluid.valves["hpcs_v_4"]["sealed_in"] = True

    #model.indicators["hpcs_init"] = hpcs_init