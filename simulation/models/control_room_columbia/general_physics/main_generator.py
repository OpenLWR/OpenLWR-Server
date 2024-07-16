from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.general_physics import main_turbine
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

    Volt, Amp, Power, Factor = getVoltageAmperesPower()

    if Generator["Synchronized"]:
        grid_frequency = 60

        main_turbine.Turbine["AngularVelocity"] = grid_frequency*math.pi
    


