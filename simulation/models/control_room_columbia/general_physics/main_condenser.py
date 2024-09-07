#import iapws
from simulation.models.control_room_columbia.reactor_physics import pressure
from simulation.models.control_room_columbia import model

MainCondenserPressure = 0 #pa
MainCondenserVolume = 928500.26 #liters #TODO: need actual size
MainCondenserAtmosphere = {
    "Nitrogen" : 850, #kg
    "Oxygen" : 0,
    "Hydrogen" : 0,
}
MainCondenserHotwellMass = 308521 #about half full?

def initalize():
    MainCondenserPressure = pressure.PartialPressure(pressure.GasTypes["Nitrogen"],MainCondenserAtmosphere["Nitrogen"],100,MainCondenserVolume)
    #print(MainCondenserPressure/6895) #PSI
    #print(MainCondenserPressure/3386) #In.Hg
    #print(abs((MainCondenserPressure/3386)-29.9212)) #In.Hg, backpressure

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

    MainCondenserPressure = pressure.PartialPressure(pressure.GasTypes["Nitrogen"],MainCondenserAtmosphere["Nitrogen"],100,MainCondenserVolume)

    #print(MainCondenserPressure/3386) #In.Hg

    #Pretend theres some amount of in-leakage
    Atmospheres = MainCondenserPressure/101325 

    if Atmospheres < 1:
        MainCondenserAtmosphere["Nitrogen"] += 100*abs(Atmospheres-1)*0.1 #Assume 500kg/s of in-leakage at 0 atm(randomize this later?)
        #TODO: The rated limit is 50 scfm. That is 1.7 kg/s of in-leakage.

        #TODO: Radiolytic decomposition of water, seperation of H2O into two hydrogens and one oxygen from radiation

    #Condenser Air Removal Pumps

    if MainCondenserPressure/3386 <= 25: #CAR can only pull around 25 in.hg and will trip at 25 in.hg
        model.pumps["car_p_1a"]["motor_breaker_closed"] = False
        model.pumps["car_p_1b"]["motor_breaker_closed"] = False

    Car1RPM = model.pumps["car_p_1a"]["rpm"]
    Car2RPM = model.pumps["car_p_1b"]["rpm"]

    Car1Flow = (Car1RPM/1800)*8.15 #very very very bad very simplify
    Car2Flow = (Car2RPM/1800)*8.15

    TotalAirRemoved = Car1Flow+Car2Flow 
    TotalAirRemoved *= 0.1 #Deltatime

    #Discharged to the Turbine Building

    MainCondenserAtmosphere["Nitrogen"] -= TotalAirRemoved

    print(MainCondenserHotwellMass)

    #Steam Jet Air Ejectors

    #Assume for now we are using the aux boilers to run the SJAEs

    

    #MainCondenserAtmosphere["Nitrogen"] -= TotalAirRemovedSJAE

    #Hotwell storage capacity is 163,000 gal


def addHotwellWater(kg):
    global MainCondenserHotwellMass
    MainCondenserHotwellMass+=kg


        





    
    
