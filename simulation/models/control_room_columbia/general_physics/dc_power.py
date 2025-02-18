def findAmpHoursToZero(amphours=1190,start_voltage=130,end_voltage=105):
    return (start_voltage/(start_voltage-end_voltage))*amphours #Not sure how accurate this is but it should be close enough for us

class Battery:
    def __init__(self,voltage,amphours):
        self.normal_amphours = amphours
        self.amphours = amphours
        self.voltage = voltage
        self.normal_voltage = voltage

    def calculate(self):

        amps = 15 #This should work for negative numbers, which is effectively charging the battery.

        amp_hours_used = (amps*0.1) #Delta time.

        amp_hours_used = (amps/3600) #To hours

        self.amphours = self.amphours-amp_hours_used

        self.voltage = (self.amphours/self.normal_amphours)*self.normal_voltage

