from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.reactor_physics import pressure

safety_relief = {
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