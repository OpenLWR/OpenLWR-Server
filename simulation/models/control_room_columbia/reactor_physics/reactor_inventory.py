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
    Volume_Of_Vessel = Volume_Of_Vessel*(1/3) #Equipment in the RPV takes up volume
    #volume = 2D Area * Height, so
    #Height = volume/2D Area
    #Because this uses volume, we can simulate water expansion.
    return ((Volume/Volume_Of_Vessel)) #we have to convert from mm to inches

def mm_to_inches(value):
    return value/25.4

rx_level_wr = 35
rx_level_nr = 35
rx_level_fzr = 35

waterMass = 928500.26*(1/3)#Equipment in the RPV takes up volume
waterMass = waterMass*(2/3) #so we start at a reasonable level
limit_press = False

def run(delta):
        
    from simulation.models.control_room_columbia.reactor_physics import reactor_physics
    from simulation.models.control_room_columbia.reactor_physics  import steam_functions
    from simulation.models.control_room_columbia.reactor_physics  import pressure
    global rx_level_wr
    global rx_level_nr
    global rx_level_fzr
    global waterMass
    global limit_press
    boilingPoint = steam_functions.getBoilingPointForWater(pressure.Pressures["Vessel"])
    vapMass = 0

    from simulation.models.control_room_columbia import model
    water_temperature = model.reactor_water_temperature

    if water_temperature > 350:
        water_temperature = 350 #The simulation breaks down (errors) after 360C.

    if waterMass <= 1:
        waterMass = 1

    if waterMass>0:
        vapMass = steam_functions.vaporize(waterMass, water_temperature, pressure.Pressures["Vessel"],delta)
        reactor_physics.kgSteam = reactor_physics.kgSteam+max(vapMass["vm"],0)

        NewPress = pressure.getPressure(reactor_physics.kgSteam, water_temperature,pressure.Volumes["Vessel"])
        pressure.Pressures["Vessel"]= NewPress
        waterMass = waterMass - max(vapMass["vm"],0)

        if limit_press and pressure.Pressures["Vessel"]/6895 >= 900:
            reactor_physics.kgSteam = 37788.89282438355

        boilingPoint = steam_functions.getBoilingPointForWater(pressure.Pressures["Vessel"])

        if water_temperature > boilingPoint:
            water_temperature = boilingPoint

    else:
        NewPress = pressure.getPressure(reactor_physics.kgSteam, water_temperature,pressure.Volumes["Vessel"])
        pressure.Pressures["Vessel"] = NewPress

    if waterMass <= 1:
        waterMass = 1


    model.reactor_water_temperature = water_temperature

    raw_level = mm_to_inches(calculate_level_cylinder(Vessel_Diameter,waterMass))
    rx_level_wr = raw_level-528.55

    rx_level_fzr = min(-110,rx_level_wr) #find the bottom of this range

    if rx_level_wr > 0:
        rx_level_nr = rx_level_wr
    else:
        rx_level_nr = 0
    
def add_water(kg:int):
    global waterMass
    waterMass+=kg

def remove_steam(amount):
    from simulation.models.control_room_columbia.reactor_physics import reactor_physics
    reactor_physics.kgSteam -= amount