from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia import rod_position_information_system
from simulation.models.control_room_columbia import reactor_protection_system
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
        "range_switch" : "irm_a_range",
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
        "range_switch" : "irm_b_range",
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
        "range_switch" : "irm_c_range",
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
        "range_switch" : "irm_d_range",
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
        "range_switch" : "irm_e_range",
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
        "range_switch" : "irm_f_range",
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
        "range_switch" : "irm_g_range",
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
        "range_switch" : "irm_h_range",
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
        "core_flow" : 98,
        "gain" : 1.0,
        "selected_rod" : "",
        "lprm_strings" : [],
        "trip_setpoint_sel" : 1,
        "bypassed" : False,
        "reference_aprm" : "A", #TODO: this can be changed?
    },
    "B" : {
        "power" : 0,
        "core_flow" : 98,
        "gain" : 1.0,
        "selected_rod" : "",
        "lprm_strings" : [],
        "trip_setpoint_sel" : 1,
        "bypassed" : False,
        "reference_aprm" : "B", #TODO: this can be changed?
    },
}

oscillation_power_range_monitors = {}

scram_reactor_a = False
scram_reactor_b = False

def run(alarms,buttons,indicators,rods,switches,values):
    global scram_reactor_a
    global scram_reactor_b
    scram_reactor_a = False
    scram_reactor_b = False

    model.alarms["rbm_downscale"]["alarm"] = False
    model.alarms["irm_downscale"]["alarm"] = False
    model.alarms["lprm_downscale"]["alarm"] = False
    model.alarms["aprm_downscale"]["alarm"] = False

    model.alarms["rbm_upscale_or_inop"]["alarm"] = False
    model.alarms["irm_upscale"]["alarm"] = False
    model.alarms["lprm_upscale"]["alarm"] = False
    model.alarms["aprm_upscale"]["alarm"] = False

    model.alarms["irm_aceg_upscl_trip_or_inop"]["alarm"] = False
    model.alarms["irm_bdfh_upscl_trip_or_inop"]["alarm"] = False

    model.alarms["aprm_bdf_upscl_trip_or_inop"]["alarm"] = False
    model.alarms["aprm_ace_upscl_trip_or_inop"]["alarm"] = False

    for srm_name in source_range_monitors:
        srm = source_range_monitors[srm_name]
        
        srm["counts"] = rods[srm["rod"]]["neutrons"]
        srm["counts"] = srm["counts"]/((srm["withdrawal_percent"]**9)+1)

        try:
            srm["counts_log"] = math.log(rods[srm["rod"]]["neutrons"]/rods[srm["rod"]]["neutrons_last"])
        except:
            pass
        if srm["counts_log"] != 0:
            srm["period"] = 1/srm["counts_log"]
        else:
            srm["period"] = math.inf
        print(srm["period"])

    for irm_name in intermediate_range_monitors:
        irm = intermediate_range_monitors[irm_name]

        #IRM should indicate around 40% range 1 at 10^5 SRM
        
        power = (rods[irm["rod"]]["neutrons"]/1000000)*40

        irm["power"] = power*abs((irm["withdrawal_percent"]/100)-1)

        irm["range"] = model.switches[irm["range_switch"]]["position"]+1

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

        #IRM trips

        ms_in_run = model.switches["reactor_mode_switch"]["position"] == 3

        if irm["power"] <= 5 and ms_in_run == False and irm["range"] != 1:
            #downscale
            model.alarms["irm_downscale"]["alarm"] = True
            reactor_protection_system.add_withdraw_block("irm_%s_upscale" % irm_name)
        else:
            reactor_protection_system.remove_withdraw_block("irm_%s_upscale" % irm_name)

        if irm["power"] >= 108 and ms_in_run == False:
            #upscale
            model.alarms["irm_upscale"]["alarm"] = True
            reactor_protection_system.add_withdraw_block("irm_%s_upscale" % irm_name)
        else:
            reactor_protection_system.remove_withdraw_block("irm_%s_upscale" % irm_name)

        if irm["power"] >= 120 and ms_in_run == False:#bypass the 0-40 scale #TODO: theres some special logic here to check if the APRM isnt downscale
            #upscale trip/inop
            if irm_name in ["A","C","E","G"]:
                model.alarms["irm_aceg_upscl_trip_or_inop"]["alarm"] = True
                scram_reactor_a = True
            else:
                model.alarms["irm_bdfh_upscl_trip_or_inop"]["alarm"] = True
                scram_reactor_b = True


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
        
        #100% range 10 IRM equals around 40% power
        average_power = average_power/(2500000000000)
        average_power = average_power*40

        lprm["A"]["power"] = average_power #TODO: all detectors of the LPRM

        if average_power < lprm["A"]["downscale_setpoint"]:
            model.alarms["lprm_downscale"]["alarm"] = True

        if average_power > lprm["A"]["upscale_setpoint"]:
            model.alarms["lprm_upscale"]["alarm"] = True

    for rbm_name in rod_block_monitors:
        rbm = rod_block_monitors[rbm_name]
        
        selected = rod_position_information_system.selected_rod
        
        if selected == "none":
            rbm["selected_rod"] = ""
            continue


        if selected != rbm["selected_rod"]:
            rbm["gain"] = 0.0
            rbm["selected_rod"] = selected
            select_groups = rod_position_information_system.select_groups
            select_group_pos = 0

            for group in select_groups:
                grp = select_groups[group]
                for rod_num in grp:
                    rod = grp[rod_num]
                    if rod == selected:
                        select_group_pos = rod_num
                        break

            directions = {}

            match select_group_pos:
                case 2:
                    directions = {
                        1 : {"x" : -2, "y" : 2},
                        2 : {"x" : 6, "y" : 2},
                        3 : {"x" : -2, "y" : -6},
                        4 : {"x" : 6, "y" : -6},
                    }
                case 1:
                    directions = {
                        1 : {"x" : -6, "y" : 2},
                        2 : {"x" : 2, "y" : 2},
                        3 : {"x" : -6, "y" : -6},
                        4 : {"x" : 2, "y" : -6},
                    }
                case 4:
                    directions = {
                        1 : {"x" : -2, "y" : 6},
                        2 : {"x" : 6, "y" : 6},
                        3 : {"x" : -2, "y" : -2},
                        4 : {"x" : 6, "y" : -2},
                    }
                case 3:
                    directions = {
                        1 : {"x" : -6, "y" : 6},
                        2 : {"x" : 2, "y" : 6},
                        3 : {"x" : -6, "y" : -2},
                        4 : {"x" : 2, "y" : -2},
                    }

            sel_x = int(selected.split("-")[0])
            sel_y = int(selected.split("-")[1])

            rbm_lprms = []

            for lprm_number in directions:
                direction = directions[lprm_number]
                lprm_x = str(sel_x+direction["x"])
                lprm_y = str(sel_y+direction["y"])

                lprm_name = "%s-%s" % (lprm_x,lprm_y)

                if lprm_name in local_power_range_monitors:
                    rbm_lprms.append(lprm_name)

            rbm["lprm_strings"] = rbm_lprms

        if len(rbm["lprm_strings"]) == 0:
            rbm["bypassed"] = True
        else:
            rbm["bypassed"] = False

        rbm_power = 0

        for lprm_string in rbm["lprm_strings"]:
            lprm_string = local_power_range_monitors[lprm_string]
            
            rbm_power += lprm_string["A"]["power"]
        if rbm["bypassed"]:
            rbm_power = 0
            rbm["gain"] = 1.0
        else:
            rbm_power = rbm_power/len(rbm["lprm_strings"])

        rbm_core_flow = rbm["core_flow"] 

        low_block_setpoint = (0.66*rbm_core_flow) + 25
        med_block_setpoint = (0.66*rbm_core_flow) + 33
        hi_block_setpoint = (0.66*rbm_core_flow) + 41

        #gain change circuit
        if rbm_power < average_power_range_monitors[rbm["reference_aprm"]]["power"] and rbm["gain"] == 0.0 and not rbm["bypassed"]:

            rbm["gain"] = average_power_range_monitors[rbm["reference_aprm"]]["power"]/rbm_power

            if (rbm_power*rbm["gain"]) < low_block_setpoint:
                rbm["trip_setpoint_sel"] = 1
            elif (rbm_power*rbm["gain"]) < med_block_setpoint:
                rbm["trip_setpoint_sel"] = 2
            else:
                rbm["trip_setpoint_sel"] = 3

        elif rbm_power >= average_power_range_monitors[rbm["reference_aprm"]]["power"] and rbm["gain"] == 0.0:

            rbm["gain"] = 1.0

            if (rbm_power*rbm["gain"]) < low_block_setpoint:
                rbm["trip_setpoint_sel"] = 1
            elif (rbm_power*rbm["gain"]) < med_block_setpoint:
                rbm["trip_setpoint_sel"] = 2
            else:
                rbm["trip_setpoint_sel"] = 3

        #TODO: "Push To Setup" pushbutton

        rbm["power"] = rbm_power*rbm["gain"]

        upscale = False
        downscale = False
        inop = False

        if rbm["power"] <= 5 and not rbm["bypassed"]:
            downscale = True

        #initiate rod blocks based on trip setpoints
        if rbm["power"] >= low_block_setpoint and rbm["trip_setpoint_sel"] == 1:
            reactor_protection_system.add_withdraw_block("rbm_%s_low_trip" % rbm_name)
            upscale = True
        else:
            reactor_protection_system.remove_withdraw_block("rbm_%s_low_trip" % rbm_name)
        
        if rbm["power"] >= med_block_setpoint and rbm["trip_setpoint_sel"] == 2:
            reactor_protection_system.add_withdraw_block("rbm_%s_med_trip" % rbm_name)
            upscale = True
        else:
            reactor_protection_system.remove_withdraw_block("rbm_%s_med_trip" % rbm_name)

        if rbm["power"] >= hi_block_setpoint:
            reactor_protection_system.add_withdraw_block("rbm_%s_high_trip" % rbm_name)
            upscale = True
        else:
            reactor_protection_system.remove_withdraw_block("rbm_%s_high_trip" % rbm_name)

        if downscale:
            model.alarms["rbm_downscale"]["alarm"] = True

        if upscale or inop:
            model.alarms["rbm_upscale_or_inop"]["alarm"] = True

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

        if Downscale:
            alarms["aprm_downscale"]["alarm"] = True

        if Upscale:
            reactor_protection_system.add_withdraw_block("APRM_UPSCALE_%s" % aprm_name)
            alarms["aprm_upscale"]["alarm"] = True
        else:
            reactor_protection_system.remove_withdraw_block("APRM_UPSCALE_%s" % aprm_name)

        if UpscaleTripOrInop:
            if aprm_name in {"A","C","E"}:
                scram_reactor_a = True
                alarms["aprm_ace_upscl_trip_or_inop"]["alarm"] = True
            else:
                scram_reactor_b = True
                alarms["aprm_bdf_upscl_trip_or_inop"]["alarm"] = True

    try:
        model.values["srm_a_counts"] = math.log(source_range_monitors["A"]["counts"])
        model.values["srm_b_counts"] = math.log(source_range_monitors["B"]["counts"])
        model.values["srm_c_counts"] = math.log(source_range_monitors["C"]["counts"])
        model.values["srm_d_counts"] = math.log(source_range_monitors["D"]["counts"])
    except:
        pass

    model.values["srm_a_period"] = source_range_monitors["A"]["counts_log"]
    model.values["srm_b_period"] = source_range_monitors["B"]["counts_log"]
    model.values["srm_c_period"] = source_range_monitors["C"]["counts_log"]
    model.values["srm_d_period"] = source_range_monitors["D"]["counts_log"]

    #TODO: fix this below this is so fucking messy

    model.values["irm_a_recorder"] = round(intermediate_range_monitors["A"]["power"],1)
    model.values["aprm_a_recorder"] = round(average_power_range_monitors["A"]["power"],1)
    model.values["irm_c_recorder"] = round(intermediate_range_monitors["C"]["power"],1)
    model.values["aprm_c_recorder"] = round(average_power_range_monitors["C"]["power"],1)

    model.values["irm_e_recorder"] = round(intermediate_range_monitors["E"]["power"],1)
    model.values["aprm_e_recorder"] = round(average_power_range_monitors["E"]["power"],1)
    model.values["irm_g_recorder"] = round(intermediate_range_monitors["G"]["power"],1)
    model.values["rbm_a_recorder"] = round(rod_block_monitors["A"]["power"],1)

    model.values["irm_b_recorder"] = round(intermediate_range_monitors["B"]["power"],1)
    model.values["aprm_b_recorder"] = round(average_power_range_monitors["B"]["power"],1)
    model.values["irm_d_recorder"] = round(intermediate_range_monitors["D"]["power"],1)
    model.values["aprm_d_recorder"] = round(average_power_range_monitors["D"]["power"],1)

    model.values["irm_f_recorder"] = round(intermediate_range_monitors["F"]["power"],1)
    model.values["aprm_f_recorder"] = round(average_power_range_monitors["F"]["power"],1)
    model.values["irm_h_recorder"] = round(intermediate_range_monitors["H"]["power"],1)
    model.values["rbm_b_recorder"] = round(rod_block_monitors["B"]["power"],1)
