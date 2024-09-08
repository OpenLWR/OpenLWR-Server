from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.general_physics import fluid

def run():
    model.values["cond_discharge_press"] = fluid.headers["condensate_discharge"]["pressure"]/6895
    model.values["cond_p_1a_amps"] = model.pumps["cond_p_1a"]["amperes"]
    model.values["cond_p_1b_amps"] = model.pumps["cond_p_1b"]["amperes"]
    model.values["cond_p_1c_amps"] = model.pumps["cond_p_1c"]["amperes"]

    model.values["cond_booster_discharge_press"] = fluid.headers["condensate_booster_discharge"]["pressure"]/6895
    model.values["cond_p_2a_amps"] = model.pumps["cond_p_2a"]["amperes"]
    model.values["cond_p_2b_amps"] = model.pumps["cond_p_2b"]["amperes"]
    model.values["cond_p_2c_amps"] = model.pumps["cond_p_2c"]["amperes"]