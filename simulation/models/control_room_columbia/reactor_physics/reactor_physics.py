import math

# Modules
from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import fuel
from simulation.models.control_room_columbia.reactor_physics import neutrons
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory



kgSteam = 10e2
kgSteamDrywell = 0

power_before_sd = 0
time_since_sd = 0

time_run = 0

def run(delta,rods):
    #TODO: Improve code quality, add comments, etc


    global time_run

    time_run+=delta

    CoreFlow = ((model.pumps["rrc_p_1a"]["flow"] + model.pumps["rrc_p_1b"]["flow"]) / 100000) * 100
    waterMass = reactor_inventory.waterMass
    old_temp = model.reactor_water_temperature
    new_temp = model.reactor_water_temperature

    avg_keff = 0
    avg_power = 0

    rod_num = 0

    rods_to_set = {}

    for rod in rods:
        rod_num+=1
        info = rods[rod]
        NeutronFlux = max(info["neutrons"], 100)

        mykEffArgs = fuel.get(waterMass, abs((info["insertion"]/48)-1), NeutronFlux, 60 ,CoreFlow)
        mykStep = mykEffArgs["kStep"]
        avg_keff += mykEffArgs["kEff"]
        if rod in rods_to_set:
            rods_to_set[rod] = max((info["neutrons"]+rods_to_set[rod])*mykStep,10)
        else:
            rods_to_set[rod] = max(info["neutrons"]*mykStep,10)

        info["measured_neutrons"] = info["neutrons"]

        energy = info["neutrons"]/(2500000000000)
        avg_power += energy
        energy = (energy*3486)#*delta # in mwt

        calories = ((energy*1000000))/185 # divide by number of rods
				
        HeatC = calories/1000
				
        TempNow = (HeatC/waterMass)*delta
		
        new_temp += TempNow

        if info["neutrons"] < 10:
            info["neutrons"] = 10

        directions = [
			{"x" : 4,"y" : 0},
			{"x" : -4,"y" : 0},
			{"x" : 0,"y" : 4},
			{"x" : 0,"y" : -4}
		]

        neighbors = []

        for direction in directions:

            dirX = direction["x"]
            dirY = direction["y"]
            
            rod_name = "%s-%s" % (str(info["x"]+dirX),str(info["y"]+dirY))
            if not rod_name in rods:
                nextPosition = {"name": "outside_core","actual_amount":info["neutrons"]*0.94,"count":0}
                #neighbors.append(nextPosition)
                continue

            if rod_name in rods_to_set:
                nextPosition = {"name": rod_name,"actual_amount":rods_to_set[rod_name],"count":rods_to_set[rod_name]}
            else:
                nextPosition = {"name": rod_name,"actual_amount":rods[rod_name]["neutrons"],"count":0} #set to 0 so the rod can add later

            neighbors.append(nextPosition)

		# simulate transfer

        for neighbor in neighbors:

            def transport_equation():
                return (info["neutrons"] - neighbor["actual_amount"])/10*mykStep

            transported = transport_equation()



            rods_to_set[neighbor["name"]] = neighbor["count"] + transported

            rods_to_set[rod] = max(rods_to_set[rod] - transported,10)


    for rod in rods_to_set:
        if rod == "outside_core":
            continue
        info = rods[rod]
        if rods_to_set[rod] < 10:
            rods_to_set[rod] = 10
        info["neutrons"] = rods_to_set[rod]


    avg_keff = avg_keff/rod_num
    avg_power = avg_power/rod_num
    avg_power = avg_power

    global time_since_sd
    global power_before_sd

    

    if avg_keff < 0.85 or avg_power < 0.02:
        #print(avg_keff)
        if time_since_sd == 0:
            print("!!! Reactor shutdown !!!")
            power_before_sd = avg_power

        time_since_sd += 0.1
    else:
        #reactor no longer shutdown
        power_before_sd = 0
        time_since_sd = 0

    #Wigner-Way formula for decay heat

    pw = power_before_sd #TODO
    t_0 = 100*86400 #100 days to seconds
    t = time_since_sd+1

    decay = 0.0622 * pw * ( ( t ** -0.2 ) - ( ( t_0 + t ) ** - 0.2 ) )

    decay *= 1.3 #slight increase for the heat of internals in the core

    heat_generated = decay*3486 #percent core power to mwt

    calories = (heat_generated*1000000)
				
    HeatC = calories/1000
				
    TempNow = (HeatC/waterMass)
				
    new_temp += TempNow

    model.reactor_water_temperature += new_temp-old_temp

    if time_run >= 1:
        time_run = 0

    