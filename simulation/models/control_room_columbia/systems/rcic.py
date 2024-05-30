from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.general_physics import fluid


def run():

    model.values["rcic_rpm"] = model.turbines["rcic_turbine"]["rpm"]

    if fluid.headers["rcic_exhaust_steam_line"]["pressure"]/6895 >= 20: #tech specs 3.3.6.1
        model.turbine["rcic_turbine"]["trip"] = True #this actually isolates RCIC, instead of tripping the turbine
