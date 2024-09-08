from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia import reactor_protection_system
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory

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
fw_valve = 30
setpoint_setdown_mode = 0 #-2 Inactive | -1 Active | >= 0 Timing 

def initialize():
    #initialize our PIDs:
    global MasterLevelController
    MasterLevelController = PID(Kp=0.12, Ki=0, Kd=0.5)
    #DT is DeltaTime (just use 1 for now)

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

    










    total_flow = 3600 #gpm

    global fw_valve

    control_signal = MasterLevelController.update(actual_setpoint,reactor_inventory.rx_level_wr,1)

    #TODO: use actual fluid physics

    fw_valve = max(min(fw_valve+control_signal,100),0)
    total_flow = total_flow*(fw_valve/100)

    reactor_inventory.add_water(total_flow)



    


    

    