from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia import neutron_monitoring

srm_selected = []
irm_selected = []
currently_pressed = []

def run():
    global srm_selected
    global irm_selected
    global currently_pressed
    for srm_name in neutron_monitoring.source_range_monitors:
        if not "SELECT_SRM_%s" % srm_name in model.buttons:
            continue

        model.indicators["SELECT_SRM_%s" % srm_name] = srm_name in srm_selected

        button = model.buttons["SELECT_SRM_%s" % srm_name]
        if button["state"] and (not srm_name in currently_pressed):
            if srm_name in srm_selected:
                srm_selected.remove(srm_name)
            else:
                srm_selected.append(srm_name)
            currently_pressed.append(srm_name)
        elif (not button["state"]) and srm_name in currently_pressed:
            currently_pressed.remove(srm_name)

        model.indicators["SRM_%s_POS_OUT" % srm_name] = neutron_monitoring.source_range_monitors[srm_name]["withdrawal_percent"] >= 100
        model.indicators["SRM_%s_POS_IN" % srm_name] = neutron_monitoring.source_range_monitors[srm_name]["withdrawal_percent"] <= 0


    for irm_name in neutron_monitoring.intermediate_range_monitors:
        if "SELECT_IRM_%s" % irm_name not in model.buttons:
            continue

        button = model.buttons["SELECT_IRM_%s" % irm_name]

        model.indicators["SELECT_IRM_%s" % irm_name] = irm_name in irm_selected

        if button["state"] and (not irm_name in currently_pressed):
            if irm_name in irm_selected:
                irm_selected.remove(irm_name)
            else:
                irm_selected.append(irm_name)
            currently_pressed.append(irm_name)
        elif (not button["state"]) and irm_name in currently_pressed:
            currently_pressed.remove(irm_name)

        model.indicators["IRM_%s_POS_OUT" % irm_name] = neutron_monitoring.intermediate_range_monitors[irm_name]["withdrawal_percent"] >= 100
        model.indicators["IRM_%s_POS_IN" % irm_name] = neutron_monitoring.intermediate_range_monitors[irm_name]["withdrawal_percent"] <= 0

    if model.buttons["DET_DRIVE_IN"]["state"]:
        for detector in srm_selected:
            srm = neutron_monitoring.source_range_monitors[detector]
            srm["withdrawal_percent"] = min(max(srm["withdrawal_percent"]-0.0416,0),100)

        for detector in irm_selected:
            irm = neutron_monitoring.intermediate_range_monitors[detector]
            irm["withdrawal_percent"] = min(max(irm["withdrawal_percent"]-0.0416,0),100)

    elif model.buttons["DET_DRIVE_OUT"]["state"]:
        for detector in srm_selected:
            srm = neutron_monitoring.source_range_monitors[detector]
            srm["withdrawal_percent"] = min(max(srm["withdrawal_percent"]+0.0416,0),100)

        for detector in irm_selected:
            irm = neutron_monitoring.intermediate_range_monitors[detector]
            irm["withdrawal_percent"] = min(max(irm["withdrawal_percent"]+0.0416,0),100)
