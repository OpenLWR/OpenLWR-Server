
from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.general_physics import ac_power
from simulation.models.control_room_columbia.general_physics import diesel_generator



def run():

    if model.switches["cb_dg1_7_mode"]["position"] == 0: #Switch in C.R.
        if model.switches["cb_dg1_7"]["position"] == 0:
            ac_power.breakers["cb_dg1_7"].open()
        elif model.switches["cb_dg1_7"]["position"] == 2 and ac_power.breakers["cb_dg1_7"].info["sync"]:
            ac_power.breakers["cb_dg1_7"].close()

    if model.switches["dg1_gov"]["position"] == 0:
        diesel_generator.dg1.dg["rpm_set"] -= 0.1
    elif model.switches["dg1_gov"]["position"] == 2:
        diesel_generator.dg1.dg["rpm_set"] += 0.1