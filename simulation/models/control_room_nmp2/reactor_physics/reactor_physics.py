import math

# Modules
from simulation.models.control_room_nmp2.reactor_physics import fuel
from simulation.models.control_room_nmp2.reactor_physics import neutrons

#local Heat = require(script.Parent.Heat)

waterMass = 479345
steps = 0

def run(rods):
    #TODO: Improve code quality, add comments, etc
    #NOTE: this is all very delicate, please do not mess with any of this. if you PR a commit to this, i will review it
    reactivityRate = 0

    CoreFlow = 100
    global waterMass
    period = 1
    global steps

    steps = steps+1
    if steps > 10: steps = 0

    total_power = 0
    srm_power = 0
    srm_last = 0
    rod_num = 0

    for rod in rods:
        rod_num+=1
        info = rods[rod]
        NeutronFlux = max(info["neutrons"], 100)

        mykEffArgs = fuel.get(waterMass, abs((info["insertion"]/48)-1), NeutronFlux, 60 ,CoreFlow,info["neutrons"])
        mykStep = mykEffArgs["kStep"]
        info["neutrons"] = info["neutrons"]*mykStep
        info["neutrons"] = max(info["neutrons"],100)
        #print(info["neutrons"])
        if steps == 10:
            try:
                period = 1/math.log(info["neutrons"]/max(info["neutrons_last"],1))
            except Exception:
                 period = math.inf
                
            #print(info["neutrons"])      

        total_power += info["neutrons"]/(320e15*0.7*100)
        srm_power += info["neutrons"]
        srm_last += info["neutrons_last"]
        info["neutrons_last"] = info["neutrons"]
        reactionRate = neutrons.getReactionRate(
			neutrons.getNeutronFlux(info["neutrons"], neutrons.getNeutronVelocity(neutrons.getNeutronEnergy(22))),
			mykEffArgs["MacroU235"]
		)
        reactivityRate += reactionRate
		#avgThermalPower += Neutrons.getThermalPower(reactionRate, 2000)
        directions = [
			{"x" : 4,"y" : 0},
			{"x" : -4,"y" : 0},
			{"x" : 0,"y" : 4},
			{"x" : 0,"y" : -4}
		]
        #TODO: fix this
        #there is something weird with this, and its preventing any of the code from working. Just dont use this for now.
        #NOTE: (we kind of need this part, as it spreads the neutrons around the core. I'll look into it more later.)
        #NOTE: if you are delfino stop looking at my code you bitch
        #NOTE: this code is deprecated, look at control_room_columbia dumbass
        """for direction in directions:

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
                #info["neutrons"] = abs(neutronDensity)
			
                energy = info["neutrons"]/(320e15*0.7*100)
                energy = (energy*3486) # in mwt

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
                continue"""
    
    #TODO: individual SRM detectors

    from simulation.models.control_room_nmp2 import model
    srm_power = (srm_power/rod_num)
    srm_last = (srm_last/rod_num)
    model.values["srm_a_counts"] = math.log(srm_power)
    model.values["srm_b_counts"] = math.log(srm_power)
    model.values["srm_c_counts"] = math.log(srm_power)
    model.values["srm_d_counts"] = math.log(srm_power)

    model.values["srm_a_period"] = math.log(srm_power/srm_last)
    model.values["srm_b_period"] = math.log(srm_power/srm_last)
    model.values["srm_c_period"] = math.log(srm_power/srm_last)
    model.values["srm_d_period"] = math.log(srm_power/srm_last)

    #print(math.log(srm_power/srm_last))

    total_power = (total_power/rod_num)*100
    print(total_power)