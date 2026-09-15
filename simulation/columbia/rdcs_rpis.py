from server.simulation import simulation
from server import devices
from enum import Enum
from simulation.columbia.reactor import FuelAssembly
import json


class DeviceFCD(devices.DeviceBase):
    def __init__(self, name:str):
        super().__init__(device_type="FullCoreDisplay",name=name)
        self._fields = [
            devices.DeviceField("Power",0,True),
            devices.DeviceField("Fault",1,True),
            devices.DeviceField("Scram",2,""),
            devices.DeviceField("Accumulator",3,""),
            devices.DeviceField("AccumulatorAck",4,""),
            devices.DeviceField("FullIn",5,""),
            devices.DeviceField("FullOut",6,""),
            devices.DeviceField("Drift",7,""),
            devices.DeviceField("Select",8,""),
        ]

    def on_interaction(self, interaction_id, interaction_type, data):
       return (False, "No interactions permitted on this device")

class RPIS(simulation.SimulationModule):
    def __init__(self):
        super().__init__()

        self.FCD = DeviceFCD("FullCoreDisplay")
        devices.REGISTRY.add_device(self.FCD)

    def OnTick(self,world:simulation.SimulationContext,ctx:simulation.TickContext):
        reactor = world.SimulationStateRegistry.GetState("reactor")

        scram_lights = {}
        accum_lights = {}
        accum_ack_lights = {}
        fullin = {}
        fullout = {}
        drift = {}

        for c in reactor.reactor_matrix:
            for r in c:
                if type(r) != int:
                    scram_lights[r.rod_name] = True
                    accum_lights[r.rod_name] = True
                    accum_ack_lights[r.rod_name] = False
                    fullin[r.rod_name] = True
                    fullout[r.rod_name] = True
                    drift[r.rod_name] = True

        self.FCD.set_field_value(2,json.dumps(scram_lights))
        self.FCD.set_field_value(3,json.dumps(accum_lights))
        self.FCD.set_field_value(4,json.dumps(accum_ack_lights))
        self.FCD.set_field_value(5,json.dumps(fullin))
        self.FCD.set_field_value(6,json.dumps(fullout))
        self.FCD.set_field_value(7,json.dumps(drift))
        if ctx.TickIndex % 50 == 0:
            self.FCD.set_field_value(8,"26-03") 
        else:
            self.FCD.set_field_value(8,"30-03") 

        