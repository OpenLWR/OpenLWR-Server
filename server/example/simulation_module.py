from server.simulation import simulation
from server import devices
from enum import Enum

class SBMBreaker(devices.DeviceBase):
    def __init__(self, name: str):
        super().__init__(device_type="SBMBreaker",name=name)
        self._fields = [devices.DeviceField("Position",0,1),devices.DeviceField("Flag",1,1)]

    def on_interaction(self, interaction_id, interaction_type, data):
        value = getattr(data,data.WhichOneof("data"))

        if data.field == 0 and value > 2 or value < 0: return (False, "Invalid switch position")

        self.set_field_value(data.field,value)

        if self.get_field_by_id(0).value == 0: #switch flag
            self.set_field_value(1,0)
        elif self.get_field_by_id(0).value == 2:
            self.set_field_value(1,1)

        return (True, "")

class PositionType(Enum):
    Momentary = 0,
    Maintained = 1,


class SBMSelector(devices.DeviceBase):
    def __init__(self, name: str,positions:dict):
        super().__init__(device_type="SBMBreaker",name=name)
        self._fields = [devices.DeviceField("Position",0,1)]
        self.positions = positions #not sure how to do for now

    def on_interaction(self, interaction_id, interaction_type, data):
        value = getattr(data,data.WhichOneof("data"))
        self.set_field_value(data.field,value)

class Indicator(devices.DeviceBase):
    def __init__(self, name: str):
        super().__init__(device_type="Indicator",name=name)
        self._fields = [devices.DeviceField("Lit",0,False)]



class BlinkenLights(simulation.SimulationModule):
    def __init__(self):
        super().__init__()
        self.DG_1 = SBMBreaker("DG_1")
        self.DG_1_Off = Indicator("DG_1_Off")
        self.DG_1_On = Indicator("DG_1_On")
        devices.REGISTRY.add_device(self.DG_1)
        devices.REGISTRY.add_device(self.DG_1_Off)
        devices.REGISTRY.add_device(self.DG_1_On)
        self.EngineState = False

    def OnTick(self,world:simulation.SimulationContext,ctx:simulation.TickContext):

        #print(f"executed. dt:{ctx.Delta} elapsed:{ctx.Elapsed} ")
        if devices.REGISTRY.get_device(self.DG_1.device_id).get_field_by_id(0).value == 2:
            self.EngineState = True
        elif devices.REGISTRY.get_device(self.DG_1.device_id).get_field_by_id(0).value == 0:
            self.EngineState = False

        self.DG_1_Off.set_field_value(0, not self.EngineState)
        self.DG_1_On.set_field_value(0, self.EngineState)







