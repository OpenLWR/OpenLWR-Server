from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.general_physics import fluid
from simulation.models.control_room_columbia.libraries.pid import PID

crd_fic_600 = None
valve_open = 0

def initialize():
    global crd_fic_600
    crd_fic_600 = PID(Kp=0.1, Ki=0.00000001, Kd=0.15, minimum=-0.3,maximum=0.3)

def run():
    global valve_open
    model.values["crd_p_1a_amps"] = model.pumps["crd_p_1a"]["amperes"]
    model.values["crd_p_1b_amps"] = model.pumps["crd_p_1b"]["amperes"]

    model.values["crd_system_flow"] = model.pumps["crd_p_1a"]["actual_flow"] + model.pumps["crd_p_1b"]["actual_flow"]
    model.values["charge_header_pressure"] = fluid.headers["crd_discharge"]["pressure"]/6895
    model.values["drive_header_flow"] = 0 #TODO
    model.values["cooling_header_flow"] = fluid.valves["crd_v_3"]["flow"]*15.85032 #liter/s to gpm

    speed_control_signal = crd_fic_600.update(50,model.pumps["crd_p_1a"]["actual_flow"] + model.pumps["crd_p_1b"]["actual_flow"],1) #TODO: Allow changing of in-use valve

    valve_open = max(min(valve_open+speed_control_signal,100),0)

    fluid.valves["crd_fcv_2a"]["percent_open"] = valve_open




    