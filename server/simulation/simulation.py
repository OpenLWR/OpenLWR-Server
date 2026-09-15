import numpy as np
from enum import Enum
from events import Events
from abc import ABC
import time
import threading
import pickle
from pathlib import Path
from copy import deepcopy

class SimulationState(Enum):
    Created = 0,
    Running = 1,
    Paused = 2,
    Stopped = 3,

class TickContext:
    TickIndex: np.ulonglong = 0
    Delta: np.double = 0
    Elapsed: np.double = 0



class SimulationModuleData:
    pass

class SimulationStateRegistry:
    _stateRegistry = dict()

    def GetState(self,moduleName: str) -> SimulationModuleData:
        return self._stateRegistry[moduleName]

    def SetState(self,moduleName: str, data:SimulationModuleData):
        self._stateRegistry[moduleName] = data

    def Save(self,name:str = None):

        if name == None:
            name = str(time.time())

        save_path = Path(f"saves/{name}.pkl")


        with open(save_path, "wb") as outp:

            pickle.dump(self._stateRegistry,outp)

    def Load(self,name):
        #maybe include something mentioning to only open saves you trust? Pickle has some vulnerabilities iirc

        load_path = Path(f"saves/{name}.pkl")

        with open(load_path, "rb") as inp:
            test = pickle.load(inp)
            print("loaded")
            self._stateRegistry = test

class SimulationContext:
    def __init__(self):
        self.OnModuleRegister = Events()
        self.OnTick = Events() #whats the point?
        self.OnModuleUnregister = Events()

        self.Name = ""
        self.TickContext = TickContext()
        self.State = SimulationState.Created
        self.TickRate = 1/30 #60fps

        self.Modules = []
        self.SimulationThread = None
        self.SimulationStateRegistry = SimulationStateRegistry()

    def Execute(self):
        #execute modules
        dt = 0
        while self.State != SimulationState.Stopped:
            StartTime = time.perf_counter()

            self.TickContext.Delta = dt
            self.TickContext.Elapsed += dt
           

            for module in self.Modules:
                if module.NextEvalStep == 0:
                    module.OnTick(self,self.TickContext)
                elif module.NextEvalStep > 0: #only decrement when greater than 0, so modules can disable themselves at -1
                    module.NextEvalStep -= 1

            self.OnTick.on_changed(self.TickContext)
            self.TickContext.TickIndex += 1

            EndTime = time.perf_counter()
            delta = EndTime-StartTime

            if delta < self.TickRate:
                time.sleep(self.TickRate-delta)
            else:
                print(f">Simulation cannot keep up! dT:{delta}, TickRate:{self.TickRate}")

            dt = time.perf_counter() - StartTime #one last time to get total d/t


    def AddModule(self,module):
        
        self.Modules.append(module)
        module.OnRegister(self)
        self.OnModuleRegister.on_change(module)


    def RemoveModule(self,module):

        self.OnModuleUnregister.on_change(module)
        module.OnUnregister(self)
        self.Modules.remove(module)
        

    def Start(self):
        if self.State != SimulationState.Created:
            return
        
        self.SimulationThread = threading.Thread(target=self.Execute).start()
        self.State = SimulationState.Running

    def Stop():
        pass 

    def Pause():
        pass

    def Resume():
        pass


class SimulationModule: 
    def __init__(self):
        self.NextEvalStep = 0
        self.Data = SimulationModuleData()

    def OnModulesLoaded(self, world:SimulationContext): #custom, fired when all modules have loaded
        pass

    def OnRegister(self,world:SimulationContext):
        pass

    def OnTick(self,world:SimulationContext,ctx:TickContext):
        pass

    def OnUnregister(self,world:SimulationContext):
        pass

    def SetNextEvalStep(self,tickIndex:np.ulonglong):
        self.NextEvalStep=tickIndex