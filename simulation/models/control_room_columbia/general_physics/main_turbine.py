from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import pressure
from simulation.models.control_room_columbia.reactor_physics import steam_functions
from simulation.models.control_room_columbia.general_physics import fluid
import math

Turbine = {
    "RPM": 0,
    "Load": 0,
    "Frequency": 0,
    "PowerOutput": 0,
    "Voltage": 0,
    "Amperes": 0,
    "Angle": 0,
    "AngularVelocity": 0/60*(2*math.pi),
    "Torque": 0,
    "Mass": 150000,
    "Radius": 2.5,
    "Inertia": (1/2) * 13000 * 2.5**2,
    "SteamInlet": 0,
}

Generator = {
    "Synchronized" : False,
}


def run():
    
    # Calculate the acceleration
    Inertia = Turbine["Inertia"]
    # Steam Properties
    #TODO: Stop Valves
    CVCombinedFlow = fluid.valves["ms_v_gv1"]["flow"]
    steamInletMass = CVCombinedFlow*0.05*10
    steamInletPressure = pressure.Pressures["Vessel"]

    # Electrical Properties
    turbineFrequency = (Turbine["AngularVelocity"]/(math.pi))
    # Physics

    Torque = 0

    Q = 0
    R = 0.287 # kJ/kg-K (specific gas constant for water vapor)
    T1 = model.reactor_water_temperature # °C
    m_dot = steamInletMass # kg/s
    P1 = steamInletPressure
    # Calculate inlet enthalpy
    h1 = 2.512 + R*(T1+273) # kJ/kg (from steam tables)
    # Estimate isentropic efficiency
    eta_s = .9
    # Calculate outlet pressure
    P2 = P1*(1-eta_s)**(R/0.287) #This is the turbine outlet pressure, might be useful for condenser
    #Calculate outlet enthalpy
    h2_s = h1 - R*T1*math.log(P2/P1) # isentropic enthalpy drop
    h2 = h2_s + R*T1*(1-eta_s) # actual enthalpy drop

    dh = h2-h1
    cp = 2
    #Calculate turbine torque
    Q = m_dot*dh*cp*math.pi**0.5*0.5 # kW (available power)
    omega = max(Turbine["AngularVelocity"], 0) # rpm (angular velocity)
    T = Q # Nm (torque)

    Torque = T
    

    NetTorque = Torque-(((Turbine["AngularVelocity"]+(900/60*(2*math.pi)))**2*60)/5e2)
    Turbine["AngularVelocity"] += NetTorque/Inertia
    Turbine["AngularVelocity"] = max(Turbine["AngularVelocity"],0)
    Turbine["Angle"] += Turbine["AngularVelocity"]
    Turbine["Angle"] %= 360
    Turbine["Angle"] = 0
    
    Turbine["Torque"] = Q
    Turbine["RPM"] = Turbine["AngularVelocity"]*60/(2*math.pi)
    Turbine["Frequency"] = turbineFrequency

    model.values["mt_rpm"] = Turbine["RPM"] #TODO: move to DEH