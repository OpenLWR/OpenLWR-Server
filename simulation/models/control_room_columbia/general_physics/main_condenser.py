#import iapws
from simulation.models.control_room_columbia.reactor_physics import pressure


def run():
    #Condensation is:
    #Heat removed from steam (BTU/hr)
    #Latent heat of steam (BTU/lb)
    
    #Output is water in lbs/hr

    


    """CirculatingWater = 0 #gpm
    CirculatingWater = CirculatingWater*500.4 #(500.4 lb/hr per GPM), so this is lb/hr now
    #Specific heat of water is 1btu/lb/degF
    #assume a 40 degree difference in the water (Calculate this at some point) at inlet vs outlet
    DeltaT = 40
    BTUHRs = CirculatingWater*DeltaT

    #Condensation

    data = getRegion1Data(300,9481.877072) #uhhh i dont know, probably like 300c at 1.37523 psi (2.8 inHg)

    LatentHeat = data["h"]/2.326 #2.326 for btu/lb

    Condensate = BTUHRs/LatentHeat

    Condensate = Condensate/120 #to seconds
    Condensate = Condensate*0.1 #deltatime

    print(Condensate)""" #im going to cry myself to sleep tonight guys

    #Steam Jet Air Ejectors are used because of;
    #air in-leakage from packing and gasket leaks
    #radiolytic decomposition of water into h2 and o2

    #when not at power the Condenser Air Removal pumps are used (two 50% capacity)
    #CAR is not filtered through offgas, and is alarmed for high radiation at its output

    RxPress = pressure.Pressures["Vessel"] #TODO: Place this after the Main Steam Isolation Valves!!!!

    if RxPress/6895 > 300:
        #allow use of the Steam Jet Air Ejectors

        #TODO: So for right now these dont use any steam, fix this later with better code

        





    
    
