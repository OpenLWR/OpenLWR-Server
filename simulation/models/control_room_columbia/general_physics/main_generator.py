from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.general_physics import main_turbine
from simulation.models.control_room_columbia.general_physics import ac_power
import math
import log

Generator = {
    "Synchronized" : False,
}



def getVoltageAmperesPower():
    Voltage = (76.08338608)*main_turbine.Turbine["AngularVelocity"]*math.sqrt(3)
    Amperes = Voltage/8
        
    ReactivePower = 0

    ApparentPower = Voltage*Amperes
    ApparentPower = max(ApparentPower,0.1)
    KineticEnergy = (1/2) * main_turbine.Turbine["Inertia"] * main_turbine.Turbine["AngularVelocity"]/2

    RealPower = ((main_turbine.Turbine["Torque"]/3)**2)+(KineticEnergy)
    PowerFactor = RealPower/ApparentPower
    Watts = max(0, Voltage*Amperes*math.sqrt(3*PowerFactor))

    return Voltage, Amperes, Watts, PowerFactor

def run():
    
   #TODO: Volts per hertz

    Generator["Synchronized"] = ac_power.breakers["cb_4885"]["closed"] or ac_power.breakers["cb_4888"]["closed"]

    Volt, Amp, Power, Factor = getVoltageAmperesPower()

    ac_power.sources["GEN"]["voltage"] = Volt
    ac_power.sources["GEN"]["frequency"] = (main_turbine.Turbine["AngularVelocity"]/(math.pi))

    if Generator["Synchronized"] and (abs(ac_power.sources["GRID"]["phase"]-ac_power.busses["gen_bus"]["phase"]) > 10):
        #basically, when something is synchronized out of phase,
        #the bigger generator wins and forces the smaller one into phase,
        #violently...
        #in our case the grid always wins and the generator becomes a new showpiece in our parking lot
        #TODO: send the fucking turbine
        log.info("holy shit bro")




    
    


