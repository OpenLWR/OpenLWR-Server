
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
        "counts_log" : 0,
        "period" : 0,
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
        "counts_log" : 0,
        "period" : 0,
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
        "counts_log" : 0,
        "period" : 0,
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
        "counts_log" : 0,
        "period" : 0,
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

intermediate_range_monitors = {
    "A" : {
        "rod" : "18-55", #TODO: make this the average of all rods in that area
        "power" : 0,
        "range" : 1,
        "downscale_setpoint" : 5,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 120,
        "withdrawal_percent" : 0,
        "bypassed" : False,
        "chassis" : {
            "inop" : False,
            "downscale" : False,
            "upscale" : False,
            "trip" : False,
        },
    },
    "B" : {
        "rod" : "46-55", #TODO: make this the average of all rods in that area
        "power" : 0,
        "range" : 1,
        "downscale_setpoint" : 5,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 120,
        "withdrawal_percent" : 0,
        "bypassed" : False,
        "chassis" : {
            "inop" : False,
            "downscale" : False,
            "upscale" : False,
            "trip" : False,
        },
    },
    "C" : {
        "rod" : "26-39", #TODO: make this the average of all rods in that area
        "power" : 0,
        "range" : 1,
        "downscale_setpoint" : 5,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 120,
        "withdrawal_percent" : 0,
        "bypassed" : False,
        "chassis" : {
            "inop" : False,
            "downscale" : False,
            "upscale" : False,
            "trip" : False,
        },
    },
    "D" : {
        "rod" : "34-39", #TODO: make this the average of all rods in that area
        "power" : 0,
        "range" : 1,
        "downscale_setpoint" : 5,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 120,
        "withdrawal_percent" : 0,
        "bypassed" : False,
        "chassis" : {
            "inop" : False,
            "downscale" : False,
            "upscale" : False,
            "trip" : False,
        },
    },
    "E" : {
        "rod" : "34-31", #TODO: make this the average of all rods in that area
        "power" : 0,
        "range" : 1,
        "downscale_setpoint" : 5,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 120,
        "withdrawal_percent" : 0,
        "bypassed" : False,
        "chassis" : {
            "inop" : False,
            "downscale" : False,
            "upscale" : False,
            "trip" : False,
        },
    },
    "F" : {
        "rod" : "26-31", #TODO: make this the average of all rods in that area
        "power" : 0,
        "range" : 1,
        "downscale_setpoint" : 5,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 120,
        "withdrawal_percent" : 0,
        "bypassed" : False,
        "chassis" : {
            "inop" : False,
            "downscale" : False,
            "upscale" : False,
            "trip" : False,
        },
    },
    "G" : {
        "rod" : "50-15", #TODO: make this the average of all rods in that area
        "power" : 0,
        "range" : 1,
        "downscale_setpoint" : 5,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 120,
        "withdrawal_percent" : 0,
        "bypassed" : False,
        "chassis" : {
            "inop" : False,
            "downscale" : False,
            "upscale" : False,
            "trip" : False,
        },
    },
    "H" : {
        "rod" : "18-15", #TODO: make this the average of all rods in that area
        "power" : 0,
        "range" : 1,
        "downscale_setpoint" : 5,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 120,
        "withdrawal_percent" : 0,
        "bypassed" : False,
        "chassis" : {
            "inop" : False,
            "downscale" : False,
            "upscale" : False,
            "trip" : False,
        },
    },
}

local_power_range_monitors = {}

average_power_range_monitors = {
    "A" : {
        "power" : 0,
        "downscale_setpoint" : 3,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 118,
    },
    "B" : {
        "power" : 0,
        "downscale_setpoint" : 3,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 118,
    },
    "C" : {
        "power" : 0,
        "downscale_setpoint" : 3,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 118,
    },
    "D" : {
        "power" : 0,
        "downscale_setpoint" : 3,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 118,
    },
    "E" : {
        "power" : 0,
        "downscale_setpoint" : 3,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 118,
    },
    "F" : {
        "power" : 0,
        "downscale_setpoint" : 3,
        "upscale_setpoint" : 108,
        "upscale_trip_setpoint" : 118,
    },
}

rod_block_monitors = { #TODO
    "A" : {
        "power" : 0,
        "core_flow" : 0,
    }
}

oscillation_power_range_monitors = {}

def run(alarms,buttons,indicators,rods,switches,values):

    from simulation.models.control_room_columbia import model

    for srm_name in source_range_monitors:
        srm = source_range_monitors[srm_name]
        
        srm["counts"] = rods[srm["rod"]]["neutrons"]
        srm["counts"] = srm["counts"]/((srm["withdrawal_percent"]**9)+1)


        srm["counts_log"] = math.log(rods[srm["rod"]]["neutrons"]/rods[srm["rod"]]["neutrons_last"])
        if srm["counts_log"] != 0:
            srm["period"] = 1/srm["counts_log"]
        else:
            srm["period"] = math.inf

    for irm_name in intermediate_range_monitors:
        irm = intermediate_range_monitors[irm_name]
        
        irm["power"] = rods[irm["rod"]]["neutrons"]/(320e15*0.7*120)

        irm_range = 1
        #this makes it so the odd ranges are the same range as the last even range.
        if irm["range"] % 2 == 0:
            irm_range += (irm["range"]/2)
        else:
            irm_range += ((irm["range"]-1)/2)

        range_divider = (10**irm_range)

        if irm["range"] % 2 == 0:
            irm["power"] = min(irm["power"]/range_divider,125) #0-125 scale
        else:
            scale = irm["power"]/range_divider
            scale = scale/40
            scale = scale*125
            irm["power"] = min(scale,125) #0-40 scale (display shows it as if it was a 0-125 scale.)


    for lprm_name in local_power_range_monitors:
        lprm = local_power_range_monitors[lprm_name]
        x = int(lprm_name.split("-")[0])
        y = int(lprm_name.split("-")[1])

        directions = [
            {"x" : -2, "y" : 2},
            {"x" : -2, "y" : -2},
            {"x" : 2, "y" : 2},
            {"x" : 2, "y" : -2},
        ]

        average_power = 0
        directions_detected = 0

        for dir in directions:
            rod_x = str(x - dir["x"])
            rod_y = str(y - dir["y"])

            if len(rod_x) < 2:
                rod_x = "0%s" % rod_x

            if len(rod_y) < 2:
                rod_y = "0%s" % rod_y

            rod_name = "%s-%s" % (rod_x, rod_y)

            if rod_name in rods:
                directions_detected += 1
                average_power += model.rods[rod_name]["neutrons"]

        if directions_detected == 0:
            print("LPRM has zero fuel assemblies to detect! %s" % lprm_name)
            continue

        average_power = average_power/directions_detected #average them
        average_power = average_power/(320e15*0.7)

        lprm["A"]["power"] = average_power #TODO: all detectors of the LPRM

    from simulation.models.control_room_columbia import reactor_protection_system

    for aprm_name in average_power_range_monitors:
        aprm = average_power_range_monitors[aprm_name]

        #TODO: make APRMs use the individual detectors of LPRMs in the core.
        #R304B part 4, page 148.

        average_power = 0
        lprms = 0

        for lprm_name in local_power_range_monitors:
            lprms += 1
            lprm = local_power_range_monitors[lprm_name]
            average_power += lprm["A"]["power"]

        average_power = average_power/lprms

        aprm["power"] = average_power

        #TODO: logic on all NMS

        #TODO: Flow biased scram trips

        Inop = False #TODO: inop conditions

        Downscale = aprm["power"] < aprm["downscale_setpoint"]
        Upscale = aprm["power"] > aprm["upscale_setpoint"]
        UpscaleTripOrInop = aprm["power"] > aprm["upscale_trip_setpoint"] or Inop

        if switches["reactor_mode_switch"]["position"] != model.ReactorMode.RUN:
            if aprm["power"] > 12:
                Upscale = True
            if aprm["power"] > 15:
                UpscaleTripOrInop = True

        indicators["APRM_%s_DOWNSCALE" % aprm_name] = Downscale
        indicators["APRM_%s_UPSCALE" % aprm_name] = Upscale
        indicators["APRM_%s_UPSCALE_TRIP_OR_INOP" % aprm_name] = UpscaleTripOrInop

        if Upscale:
            reactor_protection_system.add_withdraw_block("APRM_UPSCALE_%s" % aprm_name)
        else:
            reactor_protection_system.remove_withdraw_block("APRM_UPSCALE_%s" % aprm_name)

        if UpscaleTripOrInop:
            reactor_protection_system.scram("APRMUpscaleTrip")


    model.values["srm_a_counts"] = math.log(source_range_monitors["A"]["counts"])
    model.values["srm_b_counts"] = math.log(source_range_monitors["B"]["counts"])
    model.values["srm_c_counts"] = math.log(source_range_monitors["C"]["counts"])
    model.values["srm_d_counts"] = math.log(source_range_monitors["D"]["counts"])

    model.values["srm_a_period"] = source_range_monitors["A"]["counts_log"]
    model.values["srm_b_period"] = source_range_monitors["B"]["counts_log"]
    model.values["srm_c_period"] = source_range_monitors["C"]["counts_log"]
    model.values["srm_d_period"] = source_range_monitors["D"]["counts_log"]

    values["aprm_temporary"] = round(average_power_range_monitors["A"]["power"])
