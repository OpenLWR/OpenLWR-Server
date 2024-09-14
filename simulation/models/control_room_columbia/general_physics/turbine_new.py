from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import pressure
from simulation.models.control_room_columbia.reactor_physics import steam_functions
from simulation.models.control_room_columbia.general_physics import fluid
from simulation.models.control_room_columbia.general_physics import main_generator
from simulation.models.control_room_columbia.general_physics import main_condenser
import math

class Turbine:
    def __init__(self,name,inlet_header,inlet_nozzle,outlet_header,pump):
        self.name = name
        self.info = {
            "RPM": 0,
            "AngularVelocity": 0,
            "Torque": 0,
            "Mass": 150000,
            "Radius": 2.5,
            "Inertia": 500 * 6.25,
            "InletHeader": inlet_header,
            "InletNozzle": inlet_nozzle,
            "OutletHeader": outlet_header,
            "Pump": pump,
        }
        turbines[name] = self

    def calculate(self):
        # Calculate the acceleration
        Inertia = self.info["Inertia"]
        # Steam Properties

        Flow = fluid.valves[self.info["InletNozzle"]]["flow"]
        steamInletMass = Flow*25
        steamInletPressure = fluid.headers[self.info["InletHeader"]]["pressure"]
        #print(steamInletPressure/6895)

        # Physics

        Torque = 0

        Q = 0
        R = 0.287 # kJ/kg-K (specific gas constant for water vapor)
        T1 = 100 # °C
        m_dot = steamInletMass # kg/s
        P1 = steamInletPressure
        # Calculate inlet enthalpy
        h1 = 2.512 + R*(T1+273) # kJ/kg (from steam tables)
        # Estimate isentropic efficiency
        eta_s = .9
        # Calculate outlet pressure
        P2 = P1*(1-eta_s)**(R/0.287) #This is the turbine outlet pressure
        #Calculate outlet enthalpy
        h2_s = h1 - R*T1*math.log(P2/P1) # isentropic enthalpy drop
        h2 = h2_s + R*T1*(1-eta_s) # actual enthalpy drop

        dh = h2-h1
        cp = 2
        #Calculate turbine torque
        Q = m_dot*dh*cp*math.pi**0.5*0.5 # kW (available power)
        omega = max(self.info["AngularVelocity"], 0) # rpm (angular velocity)
        T = Q # Nm (torque)

        Torque = T
        

        NetTorque = Torque-(((self.info["AngularVelocity"]+(900/60*(2*math.pi)))**2*60)/5e2)
        self.info["AngularVelocity"] += NetTorque/Inertia
        self.info["AngularVelocity"] = max(self.info["AngularVelocity"],0)
        
        self.info["Torque"] = Q
        self.info["RPM"] = self.info["AngularVelocity"]*60/(2*math.pi)

        model.pumps[self.info["Pump"]]["rpm"] = self.info["RPM"]

        print(self.name)
        print(self.info["RPM"])
        print("---")

turbines = {} #TODO: Move to model when done using regular turbine.py

def initialize():
    Turbine("rfw_dt_1a","rft_dt_1a_stop","ms_v_172a","a","rfw_p_1a")
    Turbine("rfw_dt_1b","rft_dt_1b_stop","ms_v_172b","a","rfw_p_1b")

def run():
    for turbine in turbines:
        turbines[turbine].calculate()