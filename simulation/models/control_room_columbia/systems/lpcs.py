from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.general_physics import fluid
from simulation.models.control_room_columbia.systems import residual_heat_removal

def run():

    model.values["lpcs_flow"] = model.pumps["lpcs_p_1"]["actual_flow"]
    model.values["lpcs_press"] = fluid.headers["lpcs_discharge_header"]["pressure"]/6895

    model.alarms["lpcs_rhr_a_actuated"]["alarm"] = residual_heat_removal.rhr_a_lpcs_init

    if residual_heat_removal.rhr_a_lpcs_init:
        if residual_heat_removal.rhr_a_lpcs_init_first:
            model.pumps["lpcs_p_1"]["motor_breaker_closed"] = True
            residual_heat_removal.rhr_a_lpcs_init_first = False
        
        fluid.valves["lpcs_v_5"]["sealed_in"] = True


    if model.pumps["lpcs_p_1"]["motor_breaker_closed"]:
        fluid.valves["lpcs_v_11"]["sealed_in"] = model.pumps["lpcs_p_1"]["actual_flow"] < 1200

    if model.buttons["lpcs_man_init"]["state"]:
        residual_heat_removal.rhr_a_lpcs_init = True
        residual_heat_removal.rhr_a_lpcs_init_first = True

    if model.buttons["lpcs_init_reset"]["state"] and reactor_inventory.rx_level_wr > -129:
        residual_heat_removal.rhr_a_lpcs_init = False
        residual_heat_removal.rhr_a_lpcs_init_first = False
        model.alarms["lpcs_rhr_a_init_rpv_level_low"]["alarm"] = False

    #automatic init RPV level low -129"
    if reactor_inventory.rx_level_wr <= -129:
        if residual_heat_removal.rhr_a_lpcs_init == False:
            residual_heat_removal.rhr_a_lpcs_init = True
            residual_heat_removal.rhr_a_lpcs_init_first = True

        model.alarms["lpcs_rhr_a_init_rpv_level_low"]["alarm"] = True

    model.indicators["lpcs_init"] = residual_heat_removal.rhr_a_lpcs_init