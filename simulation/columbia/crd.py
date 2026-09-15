from server.simulation.simulation import SimulationModule, SimulationContext, TickContext, SimulationModuleData
from server import devices
from simulation.columbia.fluid import Pump, Valve, Header

class SBMSelector(devices.DeviceBase):
    def __init__(self, name: str,start_position: int):
        super().__init__(device_type="SBMSelector",name=name)
        self._fields = [devices.DeviceField("Position",0,start_position)]

    def on_interaction(self, interaction_id, interaction_type, data):
        value = getattr(data,data.WhichOneof("data"))
        self.set_field_value(data.field,value)

        return (True, "")

class Indicator(devices.DeviceBase):
    def __init__(self, name: str):
        super().__init__(device_type="Indicator",name=name)
        self._fields = [devices.DeviceField("Lit",0,False)]


class CRD(SimulationModule):
    def __init__(self):
        super().__init__()

        self._data = SimulationModuleData()

        self.CRD_HS_P1A = SBMSelector("CRD_P_1A",1)
        self.CRD_P1A_OPEN = Indicator("CRD_P_1A_OPEN")
        self.CRD_P1A_CLOSED = Indicator("CRD_P_1A_CLOSED")
        devices.REGISTRY.add_device(self.CRD_HS_P1A)
        devices.REGISTRY.add_device(self.CRD_P1A_OPEN)
        devices.REGISTRY.add_device(self.CRD_P1A_CLOSED)

        self.CRD_HS_V3 = SBMSelector("CRD_V_3",1)
        self.CRD_V3_OPEN = Indicator("CRD_V_3_OPEN")
        self.CRD_V3_CLOSED = Indicator("CRD_V_3_CLOSED")
        devices.REGISTRY.add_device(self.CRD_HS_V3)
        devices.REGISTRY.add_device(self.CRD_V3_OPEN)
        devices.REGISTRY.add_device(self.CRD_V3_CLOSED)

    def OnModulesLoaded(self, world):
        super().OnModulesLoaded(world)

    def OnRegister(self,world:SimulationContext) -> None:

        FluidRegistry = world.SimulationStateRegistry.GetState("Fluid").FLUID_REGISTRY

        FluidRegistry.add_node(Header("CRD_Suction",101.6,5000))
        FluidRegistry.add_node(Header("CRD_Discharge",50.8,10000))
        FluidRegistry.add_node(Header("Charging_Header",50.8,2000))
        FluidRegistry.add_node(Header("CRD_Post_FCV",50.8,2000))
        FluidRegistry.add_node(Header("CRD_Cooling",50.8,2000))
        FluidRegistry.add_node(Header("CRD_Drive",25.4,2000))

        #Valves
        FluidRegistry.add_valve(Valve("COND-V-19","CST","CRD_Suction",101.6,100,))
        FluidRegistry.add_valve(Valve("TEMP_CHARGING","CRD_Discharge","Charging_Header",50.8,100)) #TODO: add "pipe" class which is a full open valve : )
        FluidRegistry.add_valve(Valve("CRD-FCV-2A","CRD_Discharge","CRD_Post_FCV",38.1,30))
        FluidRegistry.add_valve(Valve("CRD-V-3","CRD_Post_FCV","CRD_Cooling",38.1,50))
        FluidRegistry.add_valve(Valve("TEMP_COOLING","CRD_Cooling","RPV",38.1,100))
        

        #CRD Pumps
        FluidRegistry.add_pump(Pump("CRD-P-1A","CRD_Suction","CRD_Discharge",200,1450,1800,horsepower=25)) #TODO: grab real hp
        FluidRegistry.add_pump(Pump("CRD-P-1B","CRD_Suction","CRD_Discharge",200,1450,1800,horsepower=25)) #TODO: grab real hp

        world.SimulationStateRegistry.SetState("CRD",self._data)
        
    def OnTick(self,world:SimulationContext,ctx:TickContext) -> None:
        delta = ctx.Delta

        FluidRegistry = world.SimulationStateRegistry.GetState("Fluid").FLUID_REGISTRY



        print(FluidRegistry.valves["CRD-FCV-2A"].get_flow_gpm(), " FCV Flow")
        print(FluidRegistry.nodes["CRD_Discharge"].get_pressure_psig(), " CRD Discharge press")
        print(FluidRegistry.nodes["CRD_Suction"].get_pressure_psig(), " CRD Suction press")
    

        if self.CRD_HS_P1A.get_field_by_id(0).value == 0:
            FluidRegistry.get_pump("CRD-P-1A").stop()
        elif self.CRD_HS_P1A.get_field_by_id(0).value  == 2:
            FluidRegistry.get_pump("CRD-P-1A").start()

        if self.CRD_HS_V3.get_field_by_id(0).value  == 0:
            FluidRegistry.get_valve("CRD-V-3").stroke_shut(delta)
        elif self.CRD_HS_V3.get_field_by_id(0).value  == 2:
            FluidRegistry.get_valve("CRD-V-3").stroke_open(delta)

        self.CRD_P1A_CLOSED.set_field_value(0,FluidRegistry.get_pump("CRD-P-1A").running)
        self.CRD_P1A_OPEN.set_field_value(0,FluidRegistry.get_pump("CRD-P-1A").running==False)

        self.CRD_V3_CLOSED.set_field_value(0,FluidRegistry.get_valve("CRD-V-3").percent_open<100)
        self.CRD_V3_OPEN.set_field_value(0,FluidRegistry.get_valve("CRD-V-3").percent_open>0)

        
        

        






