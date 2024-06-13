from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia import reactor_protection_system
from simulation.models.control_room_columbia.general_physics import fluid
from simulation.models.control_room_columbia.reactor_physics import pressure

setpoint = 950 #pressure drop is ~ 50 psig across the main steam system


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

PressureController = None
gov_valve = 30

def initialize():
    #initialize our PIDs:
    global PressureController
    PressureController = PID(Kp=0.2, Ki=0, Kd=0.2)
    #DT is DeltaTime (just use 1 for now)

def run():

    global setpoint

    global gov_valve
    
    control_signal = PressureController.update(setpoint,fluid.headers["main_steam_line_a_tunnel"]["pressure"]/6895,1)
    #control_signal = PressureController.update(setpoint,pressure.Pressures["Vessel"]/6895,1)

    gov_valve = max(min(gov_valve-control_signal,100),0)
    print(gov_valve)
    print(fluid.headers["main_steam_line_a_tunnel"]["pressure"]/6895)
    fluid.valves["ms_v_gv1"]["percent_open"] = gov_valve
    fluid.valves["ms_v_gv2"]["percent_open"] = gov_valve
    fluid.valves["ms_v_gv3"]["percent_open"] = gov_valve
    fluid.valves["ms_v_gv4"]["percent_open"] = gov_valve



    


    

    