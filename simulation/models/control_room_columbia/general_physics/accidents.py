from simulation.models.control_room_columbia.reactor_physics import pressure
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.reactor_physics import reactor_physics
import math



def run(delta):
    if True: #un-hardcode later
        steamline_pressure = pressure.Pressures["Vessel"]
        drywell_pressure = pressure.Pressures["Drywell"]

        break_size = 80 #mm
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

