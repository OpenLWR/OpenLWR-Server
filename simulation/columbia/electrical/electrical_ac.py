# WIP by watchful
# pain

from server.simulation import simulation
from server import devices
from enum import Enum

class ElectricalLoad:
    def __init__(self):
        pass

class ElectricalConductor:
    _voltage:0
    _loads:list
    def __init__(self):
        pass

    def GetPower(self): #total power
        pass

    def GetRealPower(self):
        pass

    def GetReactivePower(self):
        pass

    def GetCurrent(self):
        pass

    def GetLoads(self):
        pass

    def GetVoltage(self):
        pass

    def GetLoads(self):
        return self._loads

    def AddLoad(self,load:ElectricalLoad):
        pass

    def AddBus(self,bus:Bus):
        pass


class Source(ElectricalConductor):
    def __init__(self):
        pass


class Bus(ElectricalConductor):
    def __init__(self):
        pass

class Breaker:
    def __init__(self):
        pass

class DHPBreaker(Breaker):
    def __init__(self):
        pass




#TODO: define devices elsewhere
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
    
class Indicator(devices.DeviceBase):
    def __init__(self, name: str):
        super().__init__(device_type="Indicator",name=name)
        self._fields = [devices.DeviceField("Lit",0,False)]

class ElectricalSystem(simulation.SimulationModule):
    _sources:list[Source]
    def __init__(self):
        super().__init__()
        self.Buses = {}
        self.Breakers = {}

        self.Sources["ashe250"] = Source()

        self.Buses["sm1"] = Bus()

        self.DG_1 = SBMBreaker("DG_1")
        self.DG_1_Off = Indicator("DG_1_Off")
        self.DG_1_On = Indicator("DG_1_On")
        devices.REGISTRY.add_device(self.DG_1)
        devices.REGISTRY.add_device(self.DG_1_Off)
        devices.REGISTRY.add_device(self.DG_1_On)
        self.EngineState = False

    def OnTick(self,world:simulation.SimulationContext,ctx:simulation.TickContext):

        for source in self.Sources.items():
            #everything is considered a load
            #send voltage to every load (including actual motors/etc, motors can then reference their own voltage)
            #yes

            #source.
            pass
