from simulation.models.control_room_columbia.reactor_physics import pressure
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.reactor_physics import reactor_physics
from simulation.models.control_room_columbia.general_physics import tank
import math

steamline_break = False

def run(delta):

    global steamline_break

    if steamline_break: #un-hardcode later
        steamline_pressure = pressure.Pressures["Vessel"]
        drywell_pressure = pressure.Pressures["Drywell"]

        break_size = 500 #mm
        break_length = 2000 #mm dont change

        break_size = break_size/2 #to radius
        break_size = break_size * 0.1 # to cm

        flow_resistance = (8 * 33 * break_length)/(math.pi*(break_size**4))

        flow = (steamline_pressure-drywell_pressure)/flow_resistance

        flow = flow/1000 # to l/s
        flow = flow * delta

        reactor_physics.kgSteamDrywell += flow

        pressure.Pressures["Drywell"] = pressure.PartialPressure(pressure.GasTypes["Steam"],reactor_physics.kgSteamDrywell,60,pressure.Volumes["Drywell"])

        reactor_inventory.remove_steam(flow)

        print(pressure.Pressures["Drywell"]/6895)

    #downcomers

    #there are 88 downcomers
    #each 23.25" diameter

    #exhaust 8ft below min level
    val = False

    if val:
        steamline_break = True

    downcomer_diameter = 23.25*25.4 #to mm from inches

    supp_pool_level = tank.tanks["Wetwell"].get_level()
    supp_pool_level = supp_pool_level/304.8 #to feet from mm

    #calculate the level of the supp pool vs the downcomer exits

    downcomer_level = 18 #maybe correct?

    felt_water_column = max(supp_pool_level - downcomer_level,0)
    water_pressure = felt_water_column * 2989.067 #ft of h2o to pascal
    total_pressure = water_pressure + pressure.Pressures["Wetwell"]

    drywell_pressure = pressure.Pressures["Drywell"]

    downcomer_r = downcomer_diameter/2
    downcomer_r = downcomer_r *0.1 # to cm

    downcomer_length = 2000 #dont change

    flow_resistance = (8 * 33 * downcomer_length)/(math.pi*(downcomer_r**4))

    flow = (drywell_pressure-total_pressure)/flow_resistance

    flow = flow/1000 # to l/s
    flow = flow * delta

    if flow > 0 and reactor_physics.kgSteamDrywell-flow > 0:
        #cant reverse flow
        reactor_physics.kgSteamDrywell -= flow
        tank.tanks["Wetwell"].add_water(flow) #100% efficiency for now







    




    

