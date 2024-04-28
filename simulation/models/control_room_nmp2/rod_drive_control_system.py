import math

def run(rods,buttons):
	#TODO: rod motions by the operator
    for rod in rods:
        info = rods[rod]
        

        if info["scram"]:
            #TODO: accumulator pressure and its affect on rod drive
            if info["insertion"] > 0:
                info["insertion"] = info["insertion"] - 1.6 #approximately 3 seconds to scram from full out
                info["accum_pressure"] = info["accum_pressure"] - 30 #approximately 2 seconds until the accumulator alarm activates
            else:
                info["insertion"] = 0
