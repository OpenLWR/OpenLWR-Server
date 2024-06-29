from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.reactor_physics import pressure

safety_relief = {
    "ms_rv_5b" : {
        "valve" : 1,
        "open_percent" : 0,
        "auto" : 1131,
        "safety_auto" : 1205,
        "flow" : 906250,
        "ads" : True,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_3d" : {
        "valve" : 2,
        "open_percent" : 0,
        "auto" : 1121,
        "safety_auto" : 1195,
        "flow" : 898800,
        "ads" : True,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_5c" : {
        "valve" : 3,
        "open_percent" : 0,
        "auto" : 1131,
        "safety_auto" : 1205,
        "flow" : 906250,
        "ads" : True,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_4d" : {
        "valve" : 4,
        "open_percent" : 0,
        "auto" : 1131,
        "safety_auto" : 1205,
        "flow" : 906250,
        "ads" : True,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_4b" : {
        "valve" : 5,
        "open_percent" : 0,
        "auto" : 1121,
        "safety_auto" : 1195,
        "flow" : 898800,
        "ads" : True,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_4a" : {
        "valve" : 6,
        "open_percent" : 0,
        "auto" : 1131,
        "safety_auto" : 1205,
        "flow" : 906250,
        "ads" : True,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_4c" : {
        "valve" : 7,
        "open_percent" : 0,
        "auto" : 1121,
        "safety_auto" : 1195,
        "flow" : 898800,
        "ads" : True,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_1a" : {
        "valve" : 8,
        "open_percent" : 0,
        "auto" : 1101,
        "flow" : 883950,
        "safety_auto" : 1175,
        "ads" : False,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_2b" : {
        "valve" : 9,
        "open_percent" : 0,
        "auto" : 1101,
        "flow" : 883950,
        "safety_auto" : 1175,
        "ads" : False,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_1c" : {
        "valve" : 10,
        "open_percent" : 0,
        "auto" : 1091,
        "safety_auto" : 1165,
        "flow" : 876118,
        "ads" : False,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_1b" : {
        "valve" : 11,
        "open_percent" : 0,
        "auto" : 1091,
        "flow" : 876118,
        "safety_auto" : 1165,
        "ads" : False,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_2c" : {
        "valve" : 12,
        "open_percent" : 0,
        "auto" : 1101,
        "flow" : 883950,
        "safety_auto" : 1175,
        "ads" : False,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_1d" : {
        "valve" : 13,
        "open_percent" : 0,
        "auto" : 1101,
        "flow" : 883950,
        "safety_auto" : 1175,
        "ads" : False,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_3c" : {
        "valve" : 14,
        "open_percent" : 0,
        "auto" : 1111,
        "safety_auto" : 1185,
        "flow" : 891380,
        "ads" : False,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_2d" : {
        "valve" : 15,
        "open_percent" : 0,
        "auto" : 1111,
        "safety_auto" : 1185,
        "flow" : 891380,
        "ads" : False,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_2a" : {
        "valve" : 16,
        "open_percent" : 0,
        "auto" : 1111,
        "safety_auto" : 1185,
        "flow" : 891380,
        "ads" : False,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_3b" : {
        "valve" : 17,
        "open_percent" : 0,
        "auto" : 1111,
        "safety_auto" : 1185,
        "flow" : 891380,
        "ads" : False,
        "malf_closed" : False,
        "malf_open" : False,
    },
    "ms_rv_3a" : {
        "valve" : 18,
        "open_percent" : 0,
        "auto" : 1121,
        "safety_auto" : 1195,
        "flow" : 898800,
        "ads" : False,
        "malf_closed" : False,
        "malf_open" : False,
    },
}

def run():
    for valve_name in safety_relief:
        valve = safety_relief[valve_name]
        operator_off = False
        operator_open = False
        relief_open = False
        safety_open = False
        ads_open = False

        if valve_name in model.switches:
            control_sw = model.switches[valve_name]
            if control_sw["position"] == 0:
                operator_off = True
            elif control_sw["position"] == 2:
                operator_open = True

            control_sw["lights"]["red"] =  valve["open_percent"] == 100
            control_sw["lights"]["green"] =  valve["open_percent"] != 100

        relief_open = pressure.Pressures["Vessel"]/6895 >= valve["auto"]
        safety_open = pressure.Pressures["Vessel"]/6895 >= valve["safety_auto"]

        if ((operator_open or relief_open or ads_open) and not operator_off) or (safety_open):
            valve["open_percent"] = max(min(valve["open_percent"]+10,100),0)
        else:
            valve["open_percent"] = max(min(valve["open_percent"]-10,100),0)

        SRVOutflow = ((valve["flow"]*0.000001)/(2.20462*60*0.00001*1.736842105))*(pressure.Pressures["Vessel"]/(valve["auto"]*6895))*(valve["open_percent"]/100)
        
        if SRVOutflow > 0:
            reactor_inventory.remove_steam(SRVOutflow)