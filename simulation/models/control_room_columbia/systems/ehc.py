from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.general_physics import fluid
from simulation.models.control_room_columbia.general_physics import main_turbine
from simulation.models.control_room_columbia.general_physics import main_generator
from simulation.models.control_room_columbia.general_physics import main_condenser
from simulation.models.control_room_columbia.reactor_physics import pressure
from simulation.models.control_room_columbia.libraries.pid import PID
import math

setpoint = 920

SpeedController = None
last_speed = 0

turbine_trip = False
mechanical_lockout = False

SpeedReference = {
    "ehc_closed" : -500,
    "ehc_100" : 100,
    "ehc_500" : 500,
    "ehc_1500" : 1500,
    "ehc_1800" : 1800,
    "ehc_overspeed" : 9999,
}

AccelerationReference = {
    "ehc_slow" : 10,
    "ehc_med" : 40,
    "ehc_fast" : 70,
}

LoadSetpoint = 50
SelectedSpeedReference = -500
SelectedAccelerationReference = 10

def initialize():
    #initialize our PIDs:

    global SpeedController
    SpeedController = PID(Kp=0.01, Ki=0, Kd=0.13, minimum=-10,maximum=100)

    global AccelerationController
    AccelerationController = PID(Kp=0.005, Ki=0.000001, Kd=0.22, minimum=0,maximum=10)

    global LoadController
    LoadController = PID(Kp=0.2, Ki=0.00000001, Kd=0.13, minimum=0,maximum=100)

def turbine_trips():

    global turbine_trip

    rpm = main_turbine.Turbine["RPM"]
    reset_permissive = True
 
    if rpm > 1980: #Mechanical Overspeed 110% normal (First trip)
        turbine_trip = True
        reset_permissive = False
        model.indicators["mech_trip_tripped"] = True
        model.indicators["mech_trip_resetting"] = False
        model.indicators["mech_trip_reset"] = False
    elif rpm < 1980 and rpm > 1800 and model.indicators["mech_trip_tripped"] == True:
        model.indicators["mech_trip_resetting"] = True
        reset_permissive = False
    else:
        model.indicators["mech_trip_tripped"] = False
        model.indicators["mech_trip_resetting"] = False
        model.indicators["mech_trip_reset"] = True

    if rpm > 2016: #Electrical Overspeed 112% normal (Aux trip)
        turbine_trip = True
        reset_permissive = False

    if main_condenser.MainCondenserBackPressure < 22.5: #22.5 in.hg Loss of heat sink
        turbine_trip = True
        reset_permissive = False
        model.indicators["vacuum_low"] = True
        model.indicators["vacuum_tripped"] = True
        model.indicators["vacuum_normal"] = False
        model.indicators["vacuum_reset"] = False
    else:
        model.indicators["vacuum_low"] = False
        model.indicators["vacuum_normal"] = True

    if model.buttons["mt_trip_1"]["state"]:
        turbine_trip = True

    if model.buttons["mt_reset_pb"]["state"] and reset_permissive:
        turbine_trip = False
        model.indicators["vacuum_tripped"] = False
        model.indicators["vacuum_reset"] = True

    if turbine_trip:
        model.indicators["mt_tripped"] = True
        model.indicators["mt_reset"] = False
        fluid.valves["ms_v_sv1"]["percent_open"] = min(max(fluid.valves["ms_v_sv1"]["percent_open"]-25,0),100)
        fluid.valves["ms_v_sv2"]["percent_open"] = min(max(fluid.valves["ms_v_sv2"]["percent_open"]-25,0),100)
        fluid.valves["ms_v_sv3"]["percent_open"] = min(max(fluid.valves["ms_v_sv3"]["percent_open"]-25,0),100)
        fluid.valves["ms_v_sv4"]["percent_open"] = min(max(fluid.valves["ms_v_sv4"]["percent_open"]-25,0),100)
    else:
        model.indicators["mt_tripped"] = False
        model.indicators["mt_reset"] = True
        fluid.valves["ms_v_sv1"]["percent_open"] = min(max(fluid.valves["ms_v_sv1"]["percent_open"]+25,0),100)
        fluid.valves["ms_v_sv2"]["percent_open"] = min(max(fluid.valves["ms_v_sv2"]["percent_open"]+25,0),100)
        fluid.valves["ms_v_sv3"]["percent_open"] = min(max(fluid.valves["ms_v_sv3"]["percent_open"]+25,0),100)
        fluid.valves["ms_v_sv4"]["percent_open"] = min(max(fluid.valves["ms_v_sv4"]["percent_open"]+25,0),100)

def SpeedControlUnit(rpm:int):

    global last_speed
    global SelectedSpeedReference
    global SelectedAccelerationReference

    for button in SpeedReference:
        if turbine_trip and SpeedReference[button] == -500:
            #select CV closed
            model.indicators[button] = True
            SelectedSpeedReference = -500
            continue
        elif turbine_trip:
            model.indicators[button] = False
            continue

        if model.buttons[button]["state"]:
            SelectedSpeedReference = SpeedReference[button]
            model.indicators[button] = True
            #set each other one to off
            for b in SpeedReference:
                if b != button:
                    model.indicators[b] = False

    speed_control_signal = SpeedController.update(SelectedSpeedReference,rpm,1)

    Acceleration = max((rpm-last_speed)*100,0)

    for button in AccelerationReference:
        if model.buttons[button]["state"]:
            SelectedAccelerationReference = AccelerationReference[button]
            model.indicators[button] = True
            #set each other one to off
            for b in AccelerationReference:
                if b != button:
                    model.indicators[b] = False

    acceleration_control_signal = AccelerationController.update(SelectedAccelerationReference,Acceleration,1)
    last_speed = rpm

    return max(min(speed_control_signal+acceleration_control_signal,100),0)

def PressureControlUnit(ThrottlePress:int):

    Diff = ThrottlePress-setpoint

    Demand = (Diff/30)*100

    return max(min(Demand,100),0)
    #TODO: A/B Unit

def LoadControlUnit(Load:int):

    Demand = LoadController.update(LoadSetpoint,Load,1)

    model.values["mt_load"] = Load
    model.values["mt_load_set"] = LoadSetpoint

    return Demand
    
def run():

    turbine_trips()

    #Speed Control Unit
    Speed_Control = SpeedControlUnit(main_turbine.Turbine["RPM"])

    #Pressure Control Unit
    Pressure_Control = PressureControlUnit(fluid.headers["main_steam_line_d_tunnel"]["pressure"]/6895)

    #Load Control Unit
    Load_Control = LoadControlUnit(main_generator.Generator["Output"]/1e6)


    Output = min(Speed_Control,Load_Control,Pressure_Control)

    fluid.valves["ms_v_gv1"]["percent_open"] = Output
    fluid.valves["ms_v_gv2"]["percent_open"] = Output
    fluid.valves["ms_v_gv3"]["percent_open"] = Output
    fluid.valves["ms_v_gv4"]["percent_open"] = Output

    OutputBypass = max(Pressure_Control-Output,0)

    fluid.valves["ms_v_160a"]["percent_open"] = OutputBypass
    fluid.valves["ms_v_160b"]["percent_open"] = OutputBypass
    fluid.valves["ms_v_160c"]["percent_open"] = OutputBypass
    fluid.valves["ms_v_160d"]["percent_open"] = OutputBypass