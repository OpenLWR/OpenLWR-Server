from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia import reactor_protection_system
from simulation.models.control_room_columbia.general_physics import fluid
from simulation.models.control_room_columbia.general_physics import main_turbine
from simulation.models.control_room_columbia.general_physics import main_generator
from simulation.models.control_room_columbia.general_physics import main_condenser
from simulation.models.control_room_columbia.reactor_physics import pressure
from simulation.models.control_room_columbia.libraries.pid import PID
import math

setpoint = 950 #pressure drop is ~ 50 psig across the main steam system

#Despite this being named DEH, we are using an EHC. Rename this? TODO

PressureController = None
SpeedController = None
gov_valve = 0
bypass_valve = 0
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

line_speed = {
    "on" : False, #TODO: Figure out how exactly the Line Speed Matcher works (works with the Desired Load Control?)
}

LoadSetpoint = 1100

SelectedAccelerationReference = 10

SelectedSpeedReference = -500

def initialize():
    #initialize our PIDs:
    global PressureController
    PressureController = PID(Kp=0.1, Ki=0.00000001, Kd=0.15, minimum=-0.3,maximum=0.3)

    global SpeedController
    SpeedController = PID(Kp=0.2, Ki=0.00000001, Kd=0.13, minimum=-0.04,maximum=0.03)

    global AccelerationController
    AccelerationController = PID(Kp=0.02, Ki=0.000001, Kd=0.22, minimum=-0.03,maximum=0.03)

    global LoadController
    LoadController = PID(Kp=0.2, Ki=0.00000001, Kd=0.13, minimum=0,maximum=0.04)
    #DT is DeltaTime (just use 1 for now)

def run():

    #Speed Control
    global setpoint
    global SelectedSpeedReference
    global SelectedAccelerationReference
    global LoadSetpoint

    global gov_valve
    global bypass_valve

    global last_speed
    global turbine_trip

    #Main turbine trips

    #get the Turbine Speed
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

    for button in SpeedReference:
        if model.buttons[button]["state"]:
            SelectedSpeedReference = SpeedReference[button]
            model.indicators[button] = True
            #set each other one to off
            for b in SpeedReference:
                if b != button:
                    model.indicators[b] = False

    if model.buttons["ehc_line_speed_off"]["state"]:
        line_speed["on"] = False

    if model.buttons["ehc_line_speed_selected"]["state"]:
        line_speed["on"] = True

    target_rpm = SelectedSpeedReference

    if line_speed["on"]:
        target_rpm = 60.05*math.pi
        target_rpm = target_rpm*(30/math.pi)

        model.indicators["ehc_line_speed_operating"] = True
        model.indicators["ehc_line_speed_off"] = False
    else:
        model.indicators["ehc_line_speed_operating"] = False
        model.indicators["ehc_line_speed_selected"] = False
        model.indicators["ehc_line_speed_off"] = True

    speed_control_signal = SpeedController.update(target_rpm,rpm,1)

    gov_valve = max(min(gov_valve+speed_control_signal,100),0)

    Acceleration = max((rpm-last_speed)*100,0)

    for button in AccelerationReference:
        if model.buttons[button]["state"]:
            SelectedAccelerationReference = AccelerationReference[button]
            model.indicators[button] = True
            #set each other one to off
            for b in AccelerationReference:
                if b != button:
                    model.indicators[b] = False
    if SelectedSpeedReference == -500:
        gov_valve = max(min(gov_valve-0.5,100),0)

    if main_generator.Generator["Synchronized"]:
        Load = main_generator.Generator["Output"]/1e6
        load_control_signal = LoadController.update(LoadSetpoint,Load,1)

        pressure_control_signal = PressureController.update(setpoint,pressure.Pressures["Vessel"]/6895,1)

        gov_valve = max(min(gov_valve+(load_control_signal-pressure_control_signal)-0.01,100),0)

        bypass_valve = max(bypass_valve - 0.2,0)

        #print(Load)
    else:
        acceleration_control_signal = AccelerationController.update(SelectedAccelerationReference,Acceleration,1)

        gov_valve = max(min(gov_valve+acceleration_control_signal,100),0)

        pressure_control_signal = PressureController.update(setpoint,pressure.Pressures["Vessel"]/6895,0.1)

        bypass_valve = max(min(bypass_valve-pressure_control_signal,100),0)


    fluid.valves["ms_v_gv1"]["percent_open"] = gov_valve
    fluid.valves["ms_v_gv2"]["percent_open"] = gov_valve
    fluid.valves["ms_v_gv3"]["percent_open"] = gov_valve
    fluid.valves["ms_v_gv4"]["percent_open"] = gov_valve

    fluid.valves["ms_v_160a"]["percent_open"] = bypass_valve
    fluid.valves["ms_v_160b"]["percent_open"] = bypass_valve
    fluid.valves["ms_v_160c"]["percent_open"] = bypass_valve
    fluid.valves["ms_v_160d"]["percent_open"] = bypass_valve

    last_speed = rpm
    



    


    

    