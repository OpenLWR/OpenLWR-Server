import math

# Modules
from simulation.models.control_room_columbia.reactor_physics import fuel
from simulation.models.control_room_columbia.reactor_physics import neutrons
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory



kgSteam = 10e2
steps = 0

def run(rods):
    #TODO: Improve code quality, add comments, etc
    reactivityRate = 0

    CoreFlow = 100
    waterMass = reactor_inventory.waterMass
    from simulation.models.control_room_columbia import model
    reactor_water_temperature = model.reactor_water_temperature
    period = 1
    global steps

    steps = steps+1
    if steps > 10: steps = 0

    rod_num = 0

    energy = 50 # in mwt

    calories = ((energy*1000000)*0.24) # divide by number of rods
				
    HeatC = calories/1000
				
    TempNow = (HeatC/waterMass)*0.1
				
    reactor_water_temperature += TempNow



    for rod in rods:
        rod_num+=1
        info = rods[rod]
        NeutronFlux = max(info["neutrons"], 100)
        info["neutrons_last"] = info["neutrons"]

        mykEffArgs = fuel.get(waterMass, abs((info["insertion"]/48)-1), NeutronFlux, 60 ,CoreFlow,info["neutrons"])
        mykStep = mykEffArgs["kStep"]
        info["neutrons"] = info["neutrons"]*mykStep
        info["neutrons"] = max(info["neutrons"],100)  

        reactionRate = neutrons.getReactionRate(
			neutrons.getNeutronFlux(info["neutrons"], neutrons.getNeutronVelocity(neutrons.getNeutronEnergy(22))),
			mykEffArgs["MacroU235"]
		)
        reactivityRate += reactionRate

        directions = [
			{"x" : 4,"y" : 0},
			{"x" : -4,"y" : 0},
			{"x" : 0,"y" : 4},
			{"x" : 0,"y" : -4}
		]

        energy = info["neutrons"]/(320e15*0.7*100)
        energy = (energy*3486) # in mwt

        calories = ((energy*1000000))/185 # divide by number of rods
				
        HeatC = calories/1000
				
        TempNow = (HeatC/waterMass)*0.1
				
        reactor_water_temperature += TempNow

        for direction in directions:

            dirX =direction["x"]
            dirY = direction["y"]
            neighbors = []

            try:
                nextPosition = rods["%s-%s" % (str(info["x"]+dirX),str(info["y"]+dirY))]
                neighbors.append(nextPosition)
                if info["neutrons"] < 1:
                    info["neutrons"] = 1
				
                avgNeutronEnergy = neutrons.getNeutronEnergy(22)
                neutronVelocity = neutrons.getNeutronVelocity(avgNeutronEnergy)
                neutronDensity = neutrons.getNeutronDensity(info["neutrons"], 2000)
                neutronFlux = neutrons.getNeutronFlux(neutronDensity, neutronVelocity)
                reactionRate = neutrons.getReactionRate(neutronFlux, mykEffArgs["MacroU235"])

				# simulate transfer

                for neighbor in neighbors:
                    nextPosition = neighbor
                    avgDepth = ((abs((neighbor["insertion"]/48)-1))+(abs((info["insertion"]/48)-1)))/2
                    kEffArgs = fuel.get(waterMass, abs((nextPosition["insertion"]/48)-1), NeutronFlux, 60 ,CoreFlow,info["neutrons"])
                    kStep = kEffArgs["kStep"]
                    kEff = kEffArgs["kEff"]

                    def transport_equation():
                        return (info["neutrons"] - nextPosition["neutrons"])*mykStep*kStep

                    nextPosition["neutrons"] += transport_equation()
                    info["neutrons"] -= transport_equation()
            except:
                continue

    model.reactor_water_temperature = reactor_water_temperature
    reactor_inventory.run()

    