from simulation.constants.electrical_types import ElectricalType
from simulation.constants.equipment_states import EquipmentStates
from general_physics import ac_power
from control_room_nmp2 import model

def clamp(val, clamp_min, clamp_max):
    return min(max(val,clamp_min),clamp_max)

diesel_generators = {
    "EDG1" : {
        "state" : EquipmentStates.STOPPED,
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
            "START_TROUBLE" : "edg_1_start_system_trouble",
            "RUNNING" : "edg_1_running",
            "START_TROUBLE" : "edg_1_start_system_trouble",
            "START_TROUBLE" : "edg_1_start_system_trouble",
            "START_TROUBLE" : "edg_1_start_system_trouble",
        },
    }
}

def run():
   for name in diesel_generators:
        dg = diesel_generators[name]
        match dg["state"]:
            case EquipmentStates.STARTING:
                dg["rpm"] += 7.5
                #TODO: actual start air press
                dg["start_air_press"] = 100
                if dg["rpm"] >= 900:
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

