import math

# Modules



steps = 0

Vessel_Height = 21300 #mm
Vessel_Diameter = 7450 #mm
def calculate_level_cylinder(Diameter,Volume):
	#calculate the volume of the cylinder
	#piR^2
	Volume = Volume*1000000

	Radius = Diameter/2
	Volume_Of_Vessel = (Radius*Radius)*math.pi
	#volume = 2D Area * Height, so
	#Height = volume/2D Area
	#Because this uses volume, we can simulate water expansion.
	return ((Volume/Volume_Of_Vessel)) #we have to convert from mm to inches

def mm_to_inches(value):
	return value/25.4

rx_level_wr = 35
waterMass = 928500.26

def run():
		
	from simulation.models.control_room_columbia.reactor_physics import reactor_physics
	from simulation.models.control_room_columbia.reactor_physics  import steam_functions
	from simulation.models.control_room_columbia.reactor_physics  import pressure
	global rx_level_wr
	global waterMass
	boilingPoint = steam_functions.getBoilingPointForWater(pressure.Pressures["Vessel"])
	vapMass = 0

	from simulation.models.control_room_columbia import model
	water_temperature = model.reactor_water_temperature

	if water_temperature > 350:
		water_temperature = 350 #The simulation breaks down (errors) after 360C.

	if waterMass <= 1:
		waterMass = 1

	if water_temperature > boilingPoint and waterMass>0:
		vapMass = steam_functions.vaporize(waterMass, water_temperature, pressure.Pressures["Vessel"])
		reactor_physics.kgSteam = reactor_physics.kgSteam+vapMass["vm"]
		
		NewPress = pressure.getPressure(reactor_physics.kgSteam, water_temperature,pressure.Volumes["Vessel"])
		pressure.Pressures["Vessel"]= NewPress
		waterMass = waterMass - vapMass["vm"]
	else:
		NewPress = pressure.getPressure(reactor_physics.kgSteam, water_temperature,pressure.Volumes["Vessel"])
		pressure.Pressures["Vessel"] = NewPress

	if waterMass <= 1:
		waterMass = 1

	water_temperature = boilingPoint-1

	model.reactor_water_temperature = water_temperature

	print("RX Press %s" % str(pressure.Pressures["Vessel"]/6895)) #Print pressure in PSI
	rx_level_wr = mm_to_inches(calculate_level_cylinder(Vessel_Diameter,waterMass))-310
	print("RX Level, WR %s" % str(rx_level_wr))
    