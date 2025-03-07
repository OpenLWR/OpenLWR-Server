def findAmpHoursToZero(amphours=1190,start_voltage=130,end_voltage=105):
    return (start_voltage/(start_voltage-end_voltage))*amphours #Not sure how accurate this is but it should be close enough for us

class Battery:
    def __init__(self,voltage,amphours):
        self.normal_amphours = amphours
        self.amphours = amphours
        self.voltage = voltage
        self.normal_voltage = voltage

    def whoami(self):
        return self.__class__

    def SetCharge(self,percent):
        self.amphours = self.normal_amphours*(percent/100)

    def calculate(self):

        amps = 1000 #This should work for negative numbers, which is effectively charging the battery.

        amp_hours_used = (amps*0.1) #Delta time.

        amp_hours_used = (amps/36000) #To hours

        self.amphours = self.amphours-amp_hours_used

        self.voltage = (self.amphours/self.normal_amphours)*self.normal_voltage

class Bus:
    def __init__(self,voltage):
        self.voltage = voltage
        self.normal_voltage = voltage
        self.loads = {}
        self.batteries = []
        self.feeders = []
        self.current = 0
    
    def whoami(self):
        return self.__class__

    def AddBattery(self,battery):
        self.batteries.append(battery)

    def AddFeeder(self,feeder):
        self.feeders.append(feeder)

    def AddLoad(self,load,name):
        if not name in self.loads:
            self.loads[name] = load

    def ModifyLoad(self,load,name):
        if name in self.loads:
            self.loads[name] = load

    def RemoveLoad(self,name):
        if name in self.loads:
            self.loads.pop(name)

    def calculate(self):
        a = 0

class Fuse:
    def __init__(self,disconnect_current):
        self.disconnect_current = disconnect_current
        self.current = 0
        self.running = None
        self.incoming = None
        self.closed = True

    def whoami(self):
        return self.__class__

    def SetIncoming(self,incoming):
        self.incoming = incoming

    def SetRunning(self,running):
        self.running = running

    def Repair(self):
        self.closed = True

    def calculate(self):
        if self.current >= self.disconnect_current:
            self.closed = False

class Breaker:
    def __init__(self):
        self.current = 0
        self.running = None
        self.incoming = None
        self.closed = True

    def whoami(self):
        return self.__class__

    def SetIncoming(self,incoming):
        self.incoming = incoming

    def SetRunning(self,running):
        self.running = running

    def calculate(self):
        a = 0
