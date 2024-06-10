from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.general_physics import fluid

trip_permissive_delay = -1
start_delay = -1
initiation = False

def run():

    model.values["rcic_flow"] = model.pumps["rcic_p_1"]["actual_flow"]

    model.values["rcic_rpm"] = model.turbines["rcic_turbine"]["rpm"]
    model.values["rcic_supply_press"] = fluid.headers["rcic_main_steam_line"]["pressure"]/6895
    model.values["rcic_exhaust_press"] = fluid.headers["rcic_exhaust_steam_line"]["pressure"]/6895

    model.values["rcic_pump_suct_press"] = fluid.headers["rcic_suction_header"]["pressure"]/6895
    model.values["rcic_pump_disch_press"] = fluid.headers["rcic_discharge_header"]["pressure"]/6895

    if fluid.headers["rcic_exhaust_steam_line"]["pressure"]/6895 >= 30: #tech specs 3.3.6.1
        model.turbines["rcic_turbine"]["trip"] = True #this actually isolates RCIC, instead of tripping the turbine

    #FSAR states RCIC-V-45 being NOT full closed initiates a 15 second time delay for the low suction and discharge pressure trip and;
    #initiates the startup ramp
    global start_delay
    global initiation

    #Operator stated that the signal must be in for six seconds until the valves will begin to reposition. (Seal in light wont come in until that happens)

    #forces operator to depress for six seconds until the signal comes in
    if initiation or start_delay == 0 or model.buttons["rcic_init"]["state"]:
        model.alarms["rcic_actuated"]["alarm"] = True #should this come in?
        if start_delay == -1:
            start_delay = 60
        elif start_delay > 0:
            start_delay -= 1
        elif start_delay== 0:
            model.indicators["rcic_init"] = True
            #initiation signal opens;
            # RCIC-V-45 and RCIC-V-46 and;
            # RCIC-V-13 to open, RCIC-V-13,RCIC-V-13,RCIC-V-13,RCIC-V-13 to close, SW-P-1B to start, and RRA-FN-6 to start (permissive on RCIC-V-1 and RCIC-V-45 being open) and;
            # starts the barometric condenser vacuum pump
            fluid.valves["rcic_v_45"]["sealed_in"] = True
            if fluid.valves["rcic_v_45"]["percent_open"] != 0 and fluid.valves["rcic_v_1"]["percent_open"] != 0:
                fluid.valves["rcic_v_13"]["sealed_in"] = True
    else:
        start_delay = -1
        model.alarms["rcic_actuated"]["alarm"] = False
        model.indicators["rcic_init"] = False

    if model.buttons["rcic_init_reset"]["state"] and (initiation == False and model.buttons["rcic_init"]["state"] == False):
        start_delay = -1

    model.alarms["rcic_turbine_trip"]["alarm"] = model.turbines["rcic_turbine"]["trip"]


    global trip_permissive_delay

    if model.switches["rcic_v_1"]["position"] == 0 and fluid.valves["rcic_v_1"]["percent_open"] <= 0:
        model.turbines["rcic_turbine"]["trip"] = False

    if fluid.valves["rcic_v_45"]["percent_open"] != 0 and trip_permissive_delay == -1:
        trip_permissive_delay = 150
    elif fluid.valves["rcic_v_45"]["percent_open"] != 0 and trip_permissive_delay > 0:
        trip_permissive_delay -= 1
    elif fluid.valves["rcic_v_45"]["percent_open"] != 0 and trip_permissive_delay == 0:
        #trips
        if fluid.headers["rcic_discharge_header"]["pressure"]/6895 < 400: #TODO: find actual trip setpoint
            model.turbines["rcic_turbine"]["trip"] = True
        
        if fluid.headers["rcic_discharge_header"]["pressure"]/6895 < 20: #TODO: find actual trip setpoint
            model.turbines["rcic_turbine"]["trip"] = True
    else:
        trip_permissive_delay = -1


