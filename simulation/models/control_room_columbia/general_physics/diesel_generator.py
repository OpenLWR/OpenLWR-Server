from simulation.constants.electrical_types import ElectricalType
from simulation.constants.equipment_states import EquipmentStates
from simulation.models.control_room_columbia.general_physics import ac_power
from simulation.models.control_room_columbia import model

def clamp(val, clamp_min, clamp_max):
    return min(max(val,clamp_min),clamp_max)

diesel_generators = {
    "DG1" : {
        "state" : EquipmentStates.STOPPED,
        "control_switch" : "diesel_gen_1",
        "output_breaker" : "cb_dg1_7",
        "rpm" : 0, #normal is 900
        "start_air_press" : 500,
        "auto_start" : False,
        "loca_start" : False,
        "trip" : False,
        "lockout" : False,
        #TODO: voltage regulator/rpm governor
        "voltage" : 0,
        "frequency" : 0, #8 pole generator. 60hz@900rpm
        "annunciators" : {
            "START_TROUBLE" : "dg_1_start_system_trouble",
            "RUNNING" : "dg_1_running",
        },
    },
    "DG2" : {
        "state" : EquipmentStates.STOPPED,
        "control_switch" : "diesel_gen_2",
        "output_breaker" : "cb_dg2_8",
        "rpm" : 0, #normal is 900
        "start_air_press" : 500,
        "auto_start" : False,
        "loca_start" : False,
        "trip" : False,
        "lockout" : False,
        #TODO: voltage regulator/rpm governor
        "voltage" : 0,
        "frequency" : 0, #8 pole generator. 60hz@900rpm
        "annunciators" : {
            "START_TROUBLE" : "dg_1_start_system_trouble",
            "RUNNING" : "dg_1_running",
        },
    },

}

def run():
   for name in diesel_generators:
        dg = diesel_generators[name]

        if dg["control_switch"] in model.switches:
            cont_sw = model.switches[dg["control_switch"]]

            if cont_sw["position"] == 0:
                #a loca autostart prevents this?
                if dg["state"] == EquipmentStates.RUNNING:
                    dg["state"] = EquipmentStates.STOPPING

            if cont_sw["position"] == 2:
                #TODO: flag position autostart alarm clear (and running alarm?)
                if dg["state"] == EquipmentStates.STOPPED:
                    dg["state"] = EquipmentStates.STARTING

            if "green" in cont_sw["lights"]:
                cont_sw["lights"]["green"] = dg["state"] == EquipmentStates.STOPPED
                cont_sw["lights"]["red"] = dg["state"] != EquipmentStates.STOPPED


        match dg["state"]:
            case EquipmentStates.STARTING:
                dg["rpm"] += 7.5
                #TODO: actual start air press
                dg["start_air_press"] = 100
                if dg["rpm"] >= 900:
                    #TODO: Dont close output breaker if bus is not UV'd
                    if dg["auto_start"] and not dg["loca_start"]:
                        ac_power.close_breaker(dg["output_breaker"])
                    dg["state"] = EquipmentStates.RUNNING
                    dg["rpm"] = 900

                dg["frequency"] = (dg["rpm"]*8)/120 
                dg["voltage"] = (dg["rpm"]/900)*4160 #TODO: realistic voltage
            
            case EquipmentStates.RUNNING:
                dg["start_air_press"] = 500
                dg["frequency"] = (dg["rpm"]*8)/120 
                dg["voltage"] = (dg["rpm"]/900)*4160 #TODO: realistic voltage

            case EquipmentStates.STOPPING:
                dg["start_air_press"] = 500
                dg["rpm"] -= 7.5
                if dg["rpm"] <= 0:
                    dg["state"] = EquipmentStates.STOPPED
                    dg["rpm"] = 0

                dg["frequency"] = (dg["rpm"]*8)/120 
                dg["voltage"] = (dg["rpm"]/900)*4160 #TODO: realistic voltage
                    
            case EquipmentStates.STOPPED:
                dg["frequency"] = 0
                dg["voltage"] = 0

        if name in ac_power.sources:
            ac_power.sources[name]["voltage"] = dg["voltage"]
            ac_power.sources[name]["frequency"] = dg["frequency"]
