import math

# Modules
from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import fuel
from simulation.models.control_room_columbia.reactor_physics import neutrons
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory



kgSteam = 10e2

power_before_sd = 0
time_since_sd = 0

def run(delta,rods):
    #TODO: Improve code quality, add comments, etc

    CoreFlow = ((model.pumps["rrc_p_1a"]["flow"] + model.pumps["rrc_p_1b"]["flow"]) / 100000) * 100
    waterMass = reactor_inventory.waterMass
    old_temp = model.reactor_water_temperature
    new_temp = model.reactor_water_temperature

    avg_keff = 0
    avg_power = 0

    rod_num = 0

    for rod in rods:
        rod_num+=1
        info = rods[rod]
        NeutronFlux = max(info["neutrons"], 100)
        info["neutrons_last"] = info["neutrons"]

        mykEffArgs = fuel.get(waterMass, abs((info["insertion"]/48)-1), NeutronFlux, 60 ,CoreFlow,info["neutrons"])
        mykStep = mykEffArgs["kStep"]
        avg_keff += mykEffArgs["kEff"]
        info["neutrons"] = info["neutrons"]*mykStep
        info["neutrons"] = max(info["neutrons"],100)  

        directions = [
			{"x" : 4,"y" : 0},
			{"x" : -4,"y" : 0},
			{"x" : 0,"y" : 4},
			{"x" : 0,"y" : -4}
		]

        energy = info["neutrons"]/(2500000000000)
        avg_power += energy
        energy = (energy*3486)#*delta # in mwt

        calories = ((energy*1000000))/185 # divide by number of rods
				
        HeatC = calories/1000
				
        TempNow = (HeatC/waterMass)
		
        new_temp += TempNow

        for direction in directions:

            dirX =direction["x"]
            dirY = direction["y"]
            neighbors = []

            try:
                nextPosition = rods["%s-%s" % (str(info["x"]+dirX),str(info["y"]+dirY))]
                neighbors.append(nextPosition)
                if info["neutrons"] < 1:
                    info["neutrons"] = 1


				# simulate transfer

                for neighbor in neighbors:
                    nextPosition = neighbor
                    kEffArgs = fuel.get(waterMass, abs((nextPosition["insertion"]/48)-1), NeutronFlux, 60 ,CoreFlow,info["neutrons"])
                    kStep = kEffArgs["kStep"]

                    def transport_equation():
                        return (info["neutrons"] - nextPosition["neutrons"])*mykStep*kStep

                    nextPosition["neutrons"] += transport_equation()
                    info["neutrons"] -= transport_equation()
            except:
                continue

    avg_keff = avg_keff/rod_num
    avg_power = avg_power/rod_num

    global time_since_sd
    global power_before_sd

    if avg_keff < 0.85 or avg_power < 0.02:
        #print(avg_keff)
        if time_since_sd == 0:
            print("!!! Reactor shutdown !!!")
            power_before_sd = avg_power

        time_since_sd += 0.1

    #Wigner-Way formula for decay heat

    pw = power_before_sd #TODO
    t_0 = 100*86400 #100 days to seconds
    t = time_since_sd+1

    decay = 0.0622 * pw * ( ( t ** -0.2 ) - ( ( t_0 + t ) ** - 0.2 ) )

    decay *= 3 #slight increase for the heat of internals in the core

    heat_generated = (decay/100)*3486 #percent core power to mwt

    calories = ((heat_generated*1000000))
				
    HeatC = calories/1000
				
    TempNow = (HeatC/waterMass)
				
    new_temp += TempNow

    model.reactor_water_temperature += new_temp-old_temp

    