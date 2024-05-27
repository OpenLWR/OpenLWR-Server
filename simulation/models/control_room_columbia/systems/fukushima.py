from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia import reactor_protection_system
from simulation.constants.annunciator_states import AnnunciatorStates

def run(runs):
    if runs >= 200:
        model.indicators["cr_light_normal"] = False
        model.indicators["cr_light_emergency"] = True
    
    if runs >= 230:
        reactor_protection_system.reactor_protection_systems["A"]["channel_1_trip"] = True
        reactor_protection_system.reactor_protection_systems["A"]["channel_2_trip"] = True

    if runs > 235:
        reactor_protection_system.reactor_protection_systems["B"]["channel_1_trip"] = True
        reactor_protection_system.reactor_protection_systems["B"]["channel_2_trip"] = True

    if runs >= 320:
        model.indicators["cr_light_normal"] = True
        model.indicators["cr_light_emergency"] = False

    if runs >= 390:
        model.indicators["cr_light_normal"] = False
        model.indicators["cr_light_emergency"] = True
        model.indicators["CHART_RECORDERS_OPERATE"] = False

    if runs > 420:
        model.indicators["cr_light_emergency"] = False

    if runs > 450:
        for alarm in model.alarms:
            model.alarms[alarm]["alarm"] = False
            model.alarms[alarm]["state"] = AnnunciatorStates.CLEAR

        model.indicators["SCRAM_A5"] = False
        model.indicators["SCRAM_A6"] = False
        model.indicators["SCRAM_B5"] = False
        model.indicators["SCRAM_B6"] = False

    if runs > 470:
        model.indicators["FCD_OPERATE"] = False


