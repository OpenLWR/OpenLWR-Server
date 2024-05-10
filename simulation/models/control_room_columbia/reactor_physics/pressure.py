import math

# Modules
from simulation.models.control_room_columbia.reactor_physics import fuel
from simulation.models.control_room_columbia.reactor_physics import neutrons
from simulation.models.control_room_columbia.reactor_physics import steam_functions



waterMass = 390735 #normal water level
steps = 0

Pressures = {
    "Drywell" : 0,
    "Wetwell" : 0,
    "Vessel" : 0, #pascals
}
Volumes = {
    "Drywell" : 831430.47141*2,
    "Wetwell" : 831430.47141*3,
    "Vessel" : 928500.26, #liters
}

def getPressure(steamMass, steamTemperature, volume):

    steamTemperature = 60
	
    gasConstant = 8.314
    molarMassOfSteam = 18.01528
    # Variables
    massOfSteam = (steamMass)*1000
    temperature = steamTemperature+273.15
    # Convert mass of steam to moles
    molesOfSteam = massOfSteam / molarMassOfSteam
    # Calculate the pressure using the ideal gas law
    pressure = ((molesOfSteam * gasConstant * temperature) / volume)
	
    return (pressure)

GasTypes = {
    "Steam" : 18.01528,
    "Oxygen" : 88.8102,
	"Hydrogen" : 11.1898,
	"Nitrogen" : 28.01340
}

def PartialPressure(GasType:int,Mass:int,Temperature:int,Volume:int):

    MolarMass = GasType
    GasConstant = 8.314
	
    MassGrams = Mass*1000
    MassGas = MassGrams/MolarMass
    Temperature = Temperature+273.15 #assuming C to K
	
    Pressure = ((MassGas*GasConstant*Temperature)/Volume)
	
    return Pressure

#TODO: add pressure removal