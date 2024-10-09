from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.general_physics import fluid

def run():
    if fluid.headers["sw_p_1a_discharge"]["pressure"]/6895 > 50:
        fluid.valves["sw_v_2a"]["sealed_in"] = True