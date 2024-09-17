from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia import reactor_protection_system
from simulation.models.control_room_columbia import neutron_monitoring
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.reactor_physics import pressure
from simulation.models.control_room_columbia.general_physics import fluid
#from simulation.models.control_room_columbia.libraries import transient

requested_setpoint = 35
actual_setpoint = 35


#TODO: move this somewhere better
class PID:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.last_error = 0
        self.integral = 0

    def update(self, setpoint, current, dt):
        error = setpoint-current
        derivative = (error-self.last_error)/dt
        self.integral += error * dt
        output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        self.last_error = error
        output = max(min(output,100),-100)
        return output

MasterLevelController = None
FeedA = None
FeedB = None
fw_valve = 0
FeedAValve = 0
FeedBValve = 0
setpoint_setdown_mode = 0 #-2 Inactive | -1 Active | >= 0 Timing 
#monitoring = None

def initialize():
    #initialize our PIDs:
    global MasterLevelController
    MasterLevelController = PID(Kp=0.12, Ki=0, Kd=0.5)
    #DT is DeltaTime (just use 1 for now)
    global FeedA
    FeedA = PID(Kp=0.12, Ki=0, Kd=0.5)

    global FeedB
    FeedB = PID(Kp=0.12, Ki=0, Kd=0.5)

    #global monitoring
    #monitoring = transient.Transient("Reactor Parameters")
    #monitoring.add_graph("RX POWER")
    #monitoring.add_graph("RX LEVEL")
    #monitoring.add_graph("RX PRESSURE")

rft_a_trip = False
rft_b_trip = False
rft_a_reset_timer = -1
rft_b_reset_timer = -1
tng_timer_a = -1
tnga = False #Turning gear A
tng_timer_b = -1
tngb = False #Turning gear B

def run():

    global requested_setpoint
    global actual_setpoint

    global setpoint_setdown_mode

    trip_a = (reactor_protection_system.reactor_protection_systems["A"]["channel_1_trip"] or reactor_protection_system.reactor_protection_systems["A"]["channel_2_trip"])

    trip_b = (reactor_protection_system.reactor_protection_systems["B"]["channel_1_trip"] or reactor_protection_system.reactor_protection_systems["B"]["channel_2_trip"])

    scram_signal = trip_a and trip_b

    #Setpoint setdown reduces setpoint by 18" following a scram. It is active during the whole scram. 
    #After a scram reset, the setpoint ramps up 18 inches over a 9 minute time period
    if scram_signal:
        setpoint_setdown_mode = -1

    if (not scram_signal) and setpoint_setdown_mode == -1:
        setpoint_setdown_mode = 5400

    if setpoint_setdown_mode > 0:
        setpoint_setdown_mode -= 1

    if setpoint_setdown_mode == 0:
        setpoint_setdown_mode = -2

    model.alarms["setpoint_setdown_active"]["alarm"] = setpoint_setdown_mode != -2

    if setpoint_setdown_mode >= 0:
        actual_setpoint = requested_setpoint-(18*(setpoint_setdown_mode/5400))
    elif setpoint_setdown_mode == -1:
        actual_setpoint = requested_setpoint-18
    else:
        actual_setpoint = requested_setpoint

    global fw_valve

    control_signal = MasterLevelController.update(actual_setpoint,reactor_inventory.rx_level_wr,1)

    fw_valve = max(min(fw_valve+control_signal,100),0)

    #TODO: Temporarily using the RFW Isolation valves as control valves
    fluid.valves["rfw_v_65a"]["percent_open"] = fw_valve
    fluid.valves["rfw_v_65b"]["percent_open"] = fw_valve

    global FeedAValve
    global FeedBValve

    #RFT Stop & Trip system

    global rft_a_trip
    global rft_b_trip
    global rft_a_reset_timer
    global rft_b_reset_timer

    if model.switches["rft_dt_1a_trip"]["position"] == 0:
        rft_a_trip = True
    elif model.switches["rft_dt_1a_trip"]["position"] == 2 and rft_a_reset_timer == -1:
        rft_a_reset_timer = 600 #TODO: Actually simulate this?
    elif model.switches["rft_dt_1a_trip"]["position"] == 2 and rft_a_reset_timer > 0:
        rft_a_reset_timer -= 1
    elif model.switches["rft_dt_1a_trip"]["position"] == 2 and rft_a_reset_timer <= 0:
        rft_a_trip = False
        rft_a_reset_timer = -1

    if model.switches["rft_dt_1b_trip"]["position"] == 0:
        rft_b_trip = True
    elif model.switches["rft_dt_1b_trip"]["position"] == 2 and rft_b_reset_timer == -1:
        rft_b_reset_timer = 600 #TODO: Actually simulate this?
    elif model.switches["rft_dt_1b_trip"]["position"] == 2 and rft_b_reset_timer > 0:
        rft_b_reset_timer -= 1
    elif model.switches["rft_dt_1b_trip"]["position"] == 2 and rft_b_reset_timer <= 0:
        rft_b_trip = False
        rft_b_reset_timer = -1

    #set the state of the tripe!!!!
    if rft_a_trip:
        fluid.valves["ms_v_172a"]["percent_open"] = min(max(fluid.valves["ms_v_172a"]["percent_open"]-25,0),100)
    else:
        fluid.valves["ms_v_172a"]["percent_open"] = min(max(fluid.valves["ms_v_172a"]["percent_open"]+25,0),100)
    if rft_b_trip:
        fluid.valves["ms_v_172b"]["percent_open"] = min(max(fluid.valves["ms_v_172b"]["percent_open"]-25,0),100)
    else:
        fluid.valves["ms_v_172b"]["percent_open"] = min(max(fluid.valves["ms_v_172b"]["percent_open"]+25,0),100)

    #Turning gears come on 10 seconds after HP and LPs come closed, RFT speed is LT 1 rpm, switch is in AUTO, and bearing lube oil GT 5 psig
    #Switches maintained in OFF during operation to prevent actuation during operation, and put in AUTO after RFT trip

    global tng_timer_a
    global tng_timer_b
    global tnga
    global tngb

    if fluid.valves["ms_v_172a"]["percent_open"] <= 0: #TODO: LP system
        if tng_timer_a == -1:
            tng_timer_a = 100
        elif tng_timer_a > 0:
            tng_timer_a -= 1
    else:
        tng_timer_a = -1

    if model.switches["rft_tng_1a"]["position"] == 1 and tng_timer_a <= 0 and model.pumps["rfw_p_1a"]["rpm"] < 1: #sw in auto
        tnga = True

    if model.switches["rft_tng_1a"]["position"] == 0:
        tnga = False

    if tnga:
        model.pumps["rfw_p_1a"]["rpm"] = 20
    
    model.switches["rft_tng_1a"]["lights"]["green"] = not tnga
    model.switches["rft_tng_1a"]["lights"]["red"] = tnga

    if fluid.valves["ms_v_172b"]["percent_open"] <= 0: #TODO: LP system
        if tng_timer_b == -1:
            tng_timer_b = 100
        elif tng_timer_b > 0:
            tng_timer_b -= 1
    else:
        tng_timer_b = -1

    if model.switches["rft_tng_1b"]["position"] == 1 and tng_timer_b <= 0 and model.pumps["rfw_p_1b"]["rpm"] < 1: #sw in auto
        tngb = True

    if model.switches["rft_tng_1b"]["position"] == 0:
        tngb = False

    if tngb:
        model.pumps["rfw_p_1b"]["rpm"] = 20
    
    model.switches["rft_tng_1b"]["lights"]["green"] = not tngb
    model.switches["rft_tng_1b"]["lights"]["red"] = tngb




    #RFT Governors
    control_signal_rfta = FeedA.update(5000,model.pumps["rfw_p_1a"]["rpm"],1)

    FeedAValve = max(min(FeedAValve+control_signal_rfta,100),0)

    control_signal_rftb = FeedB.update(5000,model.pumps["rfw_p_1b"]["rpm"],1)

    FeedBValve = max(min(FeedBValve+control_signal_rftb,100),0)

    fluid.valves["rft_gov_1a"]["percent_open"] = FeedAValve
    fluid.valves["rft_gov_1b"]["percent_open"] = FeedBValve

    model.values["rft_dt_1a_rpm"] = model.pumps["rfw_p_1a"]["rpm"]
    model.values["rft_dt_1b_rpm"] = model.pumps["rfw_p_1b"]["rpm"]

























    #monitoring.add("RX LEVEL",reactor_inventory.rx_level_wr)
    #monitoring.add("RX PRESSURE",pressure.Pressures["Vessel"]/6895)
    #monitoring.add("RX POWER",neutron_monitoring.average_power_range_monitors["A"]["power"])

    #valueee = False
    #a = 1
    #if valueee == True:
        #monitoring.generate_plot()
    


    


    

    