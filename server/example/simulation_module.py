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
    Momentary = 0
    Maintained = 1

class Gauge(devices.DeviceBase):
    def __init__(self, name: str):
        super().__init__(device_type="Gauge",name=name)
        self._fields = [devices.DeviceField("Value", 0, 0.0)]

class AnnunciatorState(Enum):
    Clear = 0
    Active = 1
    Acknowledged = 2
    ActiveClear = 3
        
class AnnunciatorBoard(devices.DeviceBase):
    def __init__(self, name: str, annunciators: [str]):
        super().__init__(device_type="AnnunciatorBoard",name=name)
        self._fields = [devices.DeviceField(annunciators[idx], idx, 0) for idx in range(len(annunciators))]
    def set_field_value(self, field: int, value: AnnunciatorState):
        super().set_field_value(field, value.value)
        pass

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
        self.DG_Speed = Gauge("DG_Speed")
        self.BOARD_603200 = AnnunciatorBoard("BOARD_603200", ["TEST"])
        devices.REGISTRY.add_device(self.DG_1)
        devices.REGISTRY.add_device(self.DG_1_Off)
        devices.REGISTRY.add_device(self.DG_1_On)
        devices.REGISTRY.add_device(self.DG_Speed)
        devices.REGISTRY.add_device(self.BOARD_603200)
        self.EngineState = False

    def OnTick(self,world:simulation.SimulationContext,ctx:simulation.TickContext):

        #print(f"executed. dt:{ctx.Delta} elapsed:{ctx.Elapsed} ")
        if devices.REGISTRY.get_device(self.DG_1.device_id).get_field_by_id(0).value == 2:
            self.EngineState = True
        elif devices.REGISTRY.get_device(self.DG_1.device_id).get_field_by_id(0).value == 0:
            self.EngineState = False

        if self.EngineState:
            self.DG_Speed.set_field_value(0, 1.0)
            self.BOARD_603200.set_field_value(0, AnnunciatorState.Active)
        else:
            self.DG_Speed.set_field_value(0, 0.0)
            self.BOARD_603200.set_field_value(0, AnnunciatorState.Clear)
            
        self.DG_1_Off.set_field_value(0, not self.EngineState)
        self.DG_1_On.set_field_value(0, self.EngineState)







