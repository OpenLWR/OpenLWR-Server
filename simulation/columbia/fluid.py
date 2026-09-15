from dataclasses import dataclass
from server.simulation.simulation import SimulationModule, SimulationContext, TickContext, SimulationModuleData
from enum import IntEnum
import math
from typing import Dict, Optional
from collections.abc import Callable
from dataclasses import dataclass, field


class FluidType(IntEnum):
    LIQUID = 1
    GAS = 2


class PumpType(IntEnum):
    MOTOR_DRIVEN = 0
    TURBINE_DRIVEN = 1


def clamp(val: float, clamp_min: float, clamp_max: float) -> float:
    return min(max(val, clamp_min), clamp_max)


def calculate_temperature(m1: float, m2: float, t1: float, t2: float) -> float:
    if m1 + m2 <= 0:
        return t1
    return ((m1 * t1) + (m2 * t2)) / (m1 + m2)


def get_water_vapor_pressure(temp_c: float) -> float:
    temp_c = clamp(temp_c, 0.1, 200.0)
    return 610.78 * math.exp((17.27 * temp_c) / (temp_c + 237.3))


def get_water_density(temp_c: float) -> float:
    return max(800.0, 1000.0 - 0.35 * max(0.0, temp_c - 20.0))


class FluidNode:

    def __init__(self, name: str, fluid_type: FluidType = FluidType.LIQUID, temperature: float = 60.0):
        self.name = name
        self.type = fluid_type
        self.temperature = temperature
        self.mass: float = 0.0
        self.pressure: float = 101325.0  # Pascals
        self.volume: float = float("inf")  # Volume space in Liters

    def remove_fluid(self, mass: float) -> None:
        self.mass = max(0.0, self.mass - mass)
        self.update_physics()

    def add_fluid(self, mass: float, incoming_temp: float) -> None:
        if mass > 0:
            self.temperature = calculate_temperature(self.mass, mass, self.temperature, incoming_temp)
            self.mass += mass
            self.update_physics()

    def get_pressure_psi(self) -> float:
        return self.pressure/6895

    def get_pressure_psig(self) -> float:
        return (self.pressure/6895)-14.7 # 14.7 is the normal ambient pressure for PSI

    def update_physics(self) -> None:
        pass

class Header(FluidNode):

    def __init__(
        self,
        name: str,
        diameter_mm: float,
        length_mm: float,
        fluid_type: FluidType = FluidType.LIQUID,
        temperature: float = 60.0,
    ):
        super().__init__(name, fluid_type, temperature)
        self.diameter = diameter_mm
        self.length = length_mm

        # Geometry
        radius_mm = self.diameter / 2.0
        self.volume = (math.pi * (radius_mm ** 2) * self.length) / 1e6  # Liters
        self.volume_m3 = self.volume / 1000.0

        
        rho = get_water_density(self.temperature)
        self.mass = self.volume_m3 * rho

        self.update_physics()

    def update_physics(self) -> None:
        if self.type == FluidType.LIQUID:
            rho = get_water_density(self.temperature)
            nominal_mass = max(self.volume_m3 * rho, 1e-5)

            bulk_modulus = 1.5e7 
            overfill_ratio = (self.mass - nominal_mass) / nominal_mass

            target_pressure = 101325.0 + (bulk_modulus * overfill_ratio)

            # Smooth single-step pressure transients
            if hasattr(self, 'pressure'):
                alpha = 0.2
                self.pressure = (alpha * target_pressure) + ((1.0 - alpha) * self.pressure)
            else:
                self.pressure = target_pressure

        elif self.type == FluidType.GAS:
            r_constant = 8.314
            temp_k = self.temperature + 273.15
            molar_mass = 0.018
            n_moles = self.mass / molar_mass

            if self.volume_m3 > 0:
                self.pressure = (n_moles * r_constant * temp_k) / self.volume_m3


class Tank(FluidNode):
    def __init__(
        self,
        name: str,
        total_volume_m3: float,
        cross_sectional_area_m2: float,
        initial_water_mass_kg: float,
        initial_gas_pressure_pa: float = 101325.0,
        temperature: float = 60.0,
    ):
        super().__init__(name, FluidType.LIQUID, temperature)
        self.total_volume_m3 = total_volume_m3
        self.area = cross_sectional_area_m2
        self.mass = initial_water_mass_kg
        self.gas_pressure = initial_gas_pressure_pa
        self.volume = self.total_volume_m3 * 1000.0

        self.water_level = 0.0
        self.liquid_volume_m3 = 0.0
        self.gas_volume_m3 = 0.0

        self.update_physics()

    def update_physics(self) -> None:
        rho = get_water_density(self.temperature)

        self.liquid_volume_m3 = self.mass / rho
        self.liquid_volume_m3 = min(self.liquid_volume_m3, self.total_volume_m3 * 0.999)
        self.water_level = self.liquid_volume_m3 / self.area

        self.gas_volume_m3 = max(0.001, self.total_volume_m3 - self.liquid_volume_m3)
        initial_gas_vol = max(0.001, self.total_volume_m3 - (self.mass / rho))
        self.gas_pressure = self.gas_pressure * (initial_gas_vol / self.gas_volume_m3)

        hydrostatic_head_pa = rho * 9.81 * self.water_level
        self.pressure = self.gas_pressure + hydrostatic_head_pa

@dataclass
class Valve:

    name: str
    input_node: str
    output_node: str
    diameter_mm: float
    percent_open: float = 0.0
    flow_rate: float = 0.0  # L/s
    fixed_input_pressure: Optional[float] = None
    discharge_coefficient: float = 1.0
    stroke_time_s: float = 5.0
    stroke_amount:float = field(init=False)
    def __post_init__(self):
        self.stroke_amount = 100/self.stroke_time_s

    def stroke_shut(self,delta:float) -> None:
        self.percent_open = max(0,min(100,(self.percent_open - (self.stroke_amount * delta))))
        
    def stroke_open(self,delta:float) -> None:
        self.percent_open = max(0,min(100,(self.percent_open + (self.stroke_amount * delta))))

    def set_position(self, percent: float) -> None:
        self.percent_open = clamp(percent, 0.0, 100.0)

    def get_flow_gpm(self) -> float:
        return self.flow_rate*15.850372483753

def HPCSPumpCurve(pressure_psi:float,rated_flow:float,rated_press:float) -> float:

    if pressure_psi <= 200:
        flow_gpm = ((-pressure_psi*6.25)+1250)+5000
    elif pressure_psi > 200 and pressure_psi <= 1120:
        flow_gpm = ((-pressure_psi*4.5)+900)+5000
    elif pressure_psi > 1120 and pressure_psi <= 1165:
        flow_gpm = ((-pressure_psi*8)+4820)+5000
    elif pressure_psi > 1165 and pressure_psi <= 1180:
        flow_gpm = ((-pressure_psi*33)+33945)+5000
    elif pressure_psi > 1180:
        flow_gpm = 0

    return flow_gpm

def DefaultPumpCurve(pressure_psi:float,rated_flow:float,rated_press:float) -> float:
    #we only use rated_flow and rated_press in the default pump curve (or other curve that is universal)

    pressure_psi = max(0.1,pressure_psi)

    flow_gpm = rated_flow*(rated_press/pressure_psi)

    return flow_gpm

class Pump:
    def __init__(
        self,
        name: str,
        suction_node: str,
        discharge_node: str,
        rated_flow: float,             # L/s
        rated_discharge_press: float,  # Pa
        rated_rpm: float,
        pump_type: PumpType = PumpType.MOTOR_DRIVEN,
        npshr_rated_ft: float = 25.0,
        horsepower: float = 3000.0,
        pump_curve: Callable[[float,float,float],float] = DefaultPumpCurve,
    ):
        self.name = name
        self.suction_node = suction_node
        self.discharge_node = discharge_node
        self.rated_flow = rated_flow
        self.rated_discharge_press = rated_discharge_press
        self.rated_rpm = rated_rpm
        self.pump_type = pump_type
        self.npshr_rated = npshr_rated_ft
        self.horsepower = horsepower

        self.pump_curve = pump_curve

        self.running: bool = False
        self.rpm: float = 0.0
        self.flow: float = 0.0
        self.actual_flow: float = 0.0
        self.discharge_pressure: float = 0.0

        self.npsha_ft: float = 0.0
        self.npshr_ft: float = 0.0
        self.cavitation_factor: float = 1.0

    def start(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False

    def calculate_npsh(self, suction_pressure_pa: float, fluid_temp_c: float) -> tuple[float, float, float]:
        p_sat = get_water_vapor_pressure(fluid_temp_c)
        rho = get_water_density(fluid_temp_c)

        net_suction_pa = max(0.0, suction_pressure_pa - p_sat)
        npsha_ft = (net_suction_pa / (rho * 9.81)) * 3.28084

        flow_ratio = clamp(self.actual_flow / max(self.rated_flow, 1e-5), 0.1, 1.5)
        npshr_ft = self.npshr_rated * (flow_ratio ** 2)

        if npsha_ft >= npshr_ft:
            cavitation_factor = 1.0
        elif npsha_ft <= 0.0:
            cavitation_factor = 0.0
        else:
            cavitation_factor = (npsha_ft / max(npshr_ft, 1e-5)) ** 1.5

        return npsha_ft, npshr_ft, cavitation_factor

    def update_dynamics(self, delta: float, suction_pressure: float, suction_temp: float) -> None:
        if self.pump_type == PumpType.MOTOR_DRIVEN:
            accel_step = (self.rated_rpm - self.rpm if self.running else -self.rpm) * delta
            self.rpm = clamp(self.rpm + accel_step, 0.0, self.rated_rpm)

        speed_ratio = self.rpm / max(self.rated_rpm, 1.0)
        base_flow = self.rated_flow * speed_ratio
        base_discharge_press = self.rated_discharge_press * (speed_ratio ** 2)

        self.npsha_ft, self.npshr_ft, self.cavitation_factor = self.calculate_npsh(suction_pressure, suction_temp)

        self.flow = base_flow * self.cavitation_factor
        self.discharge_pressure = base_discharge_press * self.cavitation_factor

class FluidRegistry:
    def __init__(self):
        self.nodes = dict()
        self.valves = dict()
        self.pumps = dict()

    def add_node(self, node: FluidNode) -> None:
        self.nodes[node.name] = node
    
    def add_valve(self, valve: Valve) -> None:
        self.valves[valve.name] = valve
    
    def add_pump(self, pump: Pump) -> None:
        self.pumps[pump.name] = pump

    def get_node(self, name: str) -> FluidNode:
        return self.nodes[name]

    def get_valve(self, name: str) -> Valve:
        return self.valves[name]

    def get_pump(self, name: str) -> Pump:
        return self.pumps[name]



class FluidTest(SimulationModule):

    def __init__(self):
        super().__init__()

        self._data = SimulationModuleData()

        self._data.FLUID_REGISTRY = FluidRegistry()

        #we'll create obvious fluid nodes here
        #TODO: figure real numbers here
        self._data.FLUID_REGISTRY.add_node(Tank("WETWELL", 10000, 500, 5000000)) 
        self._data.FLUID_REGISTRY.add_node(Tank("RPV", 10000, 500, 5000000,initial_gas_pressure_pa=8e+6)) #TODO: temporary gas pressure
        self._data.FLUID_REGISTRY.add_node(Tank("CST", 10000, 500, 5000000))

        """self._data.FLUID_REGISTRY.add_node(Header("HPCS_SUCT", 609.60, 5000))
        self._data.FLUID_REGISTRY.add_node(Header("HPCS_DISCH", 406.40, 10000))

        self._data.FLUID_REGISTRY.add_valve(Valve("HPCS_V_4", "HPCS_DISCH", "RPV", 406.40, 100))
        self._data.FLUID_REGISTRY.add_valve(Valve("HPCS_V_15", "WETWELL", "HPCS_SUCT", 609.60, 100))

        self._data.FLUID_REGISTRY.add_pump(Pump("HPCS_P_1", "HPCS_SUCT", "HPCS_DISCH", 394.3, 8963184.48, 1800, horsepower=3000,pump_curve=HPCSPumpCurve))"""

    def OnRegister(self,world:SimulationContext) -> None:

        world.SimulationStateRegistry.SetState("Fluid",self._data)

    def _calculate_flow_capacity(self, p1: float, p2: float, valve_cv:float ) -> float:

        specific_gravity = 1
        gal_m = valve_cv * math.sqrt((p1-p2)/specific_gravity)

        return gal_m*0.001262803
        
    def OnTick(self, world: SimulationContext, ctx: TickContext) -> None:
        delta = ctx.Delta

        self._data = world.SimulationStateRegistry.GetState("Fluid")

        for valve in self._data.FLUID_REGISTRY.valves.values():
            if valve.percent_open <= 0.0:
                valve.flow_rate = 0.0
                continue
        
            inlet = self._data.FLUID_REGISTRY.nodes.get(valve.input_node)
            outlet = self._data.FLUID_REGISTRY.nodes.get(valve.output_node)
        
            if not inlet or not outlet:
                continue
        
            inlet_press = inlet.pressure
        
            if inlet_press <= outlet.pressure or inlet.mass <= 0.0:
                valve.flow_rate = 0.0
                continue

            #Cv calculation:
            #Estimate as- Gate: 35*d^2 Ball: 22*d^2  Globe: 12*d^2
            valve.discharge_coefficient = 22*(valve.diameter_mm/25.4) #TODO: allow setting valve discharge coeff

            #Cv(t) = Cv(0) * (p/100)^1.5
            valve_cv = valve.discharge_coefficient * (valve.percent_open / 100.0)**1.5

            flow_lps = self._calculate_flow_capacity(inlet_press, outlet.pressure, valve_cv)
        
            transfer_mass = min(flow_lps * delta, inlet.mass)
        
            valve.flow_rate = transfer_mass / delta if delta > 0 else 0.0
            inlet_temp = inlet.temperature
        
            inlet.remove_fluid(transfer_mass)
            outlet.add_fluid(transfer_mass, inlet_temp)


        for pump in self._data.FLUID_REGISTRY.pumps.values():
            suction_node = self._data.FLUID_REGISTRY.nodes.get(pump.suction_node)
            discharge_node = self._data.FLUID_REGISTRY.nodes.get(pump.discharge_node)

            if not suction_node or not discharge_node:
                continue

            pump.update_dynamics(
                delta=delta,
                suction_pressure=suction_node.pressure,
                suction_temp=suction_node.temperature
            )

            if pump.flow <= 0.0:
                pump.actual_flow = 0.0
                continue

            if pump.discharge_pressure*6895 > discharge_node.pressure:
                transfer_mass = min(pump.flow * delta * 0.0630902, suction_node.mass)
                max_transfer = pump.pump_curve((discharge_node.pressure/6895),pump.rated_flow,pump.rated_discharge_press)*delta*0.0630902
                transfer_mass = max(min(max_transfer,transfer_mass),0)

                suction_node.remove_fluid(transfer_mass)
                discharge_node.add_fluid(transfer_mass, suction_node.temperature)

                pump.actual_flow = transfer_mass / delta if delta > 0 else 0.0
            else:
                pump.actual_flow = 0.0

            

            