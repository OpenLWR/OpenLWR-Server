
from simulation.constants.annunciator_states import AnnunciatorStates
import math

rps_a_trip = False
rps_b_trip = False
withdraw_block = False
insert_block = False

source_range_monitors = {
    "A" : {
        "rod" : "18-47", #TODO: make this the average of all rods in that area
        "counts" : 0,
        "withdrawal_percent" : 0,
        "associated_irms" : ["C","E"],
        "bypassed" : False,
        "chassis" : {
            "inop" : False,
            "downscale" : False,
            "upscale" : False,
            "trip" : False,
            "period" : False,
            "retract" : False,
        },
    },
    "B" : {
        "rod" : "42-47", #TODO: make this the average of all rods in that area
        "counts" : 0,
        "withdrawal_percent" : 0,
        "associated_irms" : ["C","E"],
        "bypassed" : False,
        "chassis" : {
            "inop" : False,
            "downscale" : False,
            "upscale" : False,
            "trip" : False,
            "period" : False,
            "retract" : False,
        },
    },
    "C" : {
        "rod" : "18-23", #TODO: make this the average of all rods in that area
        "counts" : 0,
        "withdrawal_percent" : 0,
        "associated_irms" : ["C","E"],
        "bypassed" : False,
        "chassis" : {
            "inop" : False,
            "downscale" : False,
            "upscale" : False,
            "trip" : False,
            "period" : False,
            "retract" : False,
        },
    },
    "D" : {
        "rod" : "42-23", #TODO: make this the average of all rods in that area
        "counts" : 0,
        "withdrawal_percent" : 0,
        "associated_irms" : ["C","E"],
        "bypassed" : False,
        "chassis" : {
            "inop" : False,
            "downscale" : False,
            "upscale" : False,
            "trip" : False,
            "period" : False,
            "retract" : False,
        },
    },

}

intermediate_range_monitors = {}

local_power_range_monitors = {}

average_power_range_monitors = {}

oscillation_power_range_monitors = {}

def run(alarms,buttons,indicators,rods,switches,values):

    from simulation.models.control_room_columbia import model
    total_power = 0
    srm_power = 0
    srm_last = 0

    for rod_name in rods:
        rod = rods[rod_name]
        total_power += rod["neutrons"]/(320e15*0.7*100)
        srm_power += rod["neutrons"]+20
        srm_last += rod["neutrons_last"]+20

    for srm_name in source_range_monitors:
        srm = source_range_monitors[srm_name]

    srm_power = (srm_power/185)
    srm_last = (srm_last/185)
    model.values["srm_a_counts"] = math.log(srm_power)
    model.values["srm_b_counts"] = math.log(srm_power)
    model.values["srm_c_counts"] = math.log(srm_power)
    model.values["srm_d_counts"] = math.log(srm_power)

    model.values["srm_a_period"] = math.log(srm_power/srm_last)
    model.values["srm_b_period"] = math.log(srm_power/srm_last)
    model.values["srm_c_period"] = math.log(srm_power/srm_last)
    model.values["srm_d_period"] = math.log(srm_power/srm_last)

    #print(math.log(srm_power/srm_last))

    total_power = (total_power/185)*100
    values["aprm_temporary"] = round(total_power)
    print(total_power)
