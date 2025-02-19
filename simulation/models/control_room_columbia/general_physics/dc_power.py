def findAmpHoursToZero(amphours=1190,start_voltage=130,end_voltage=105):
    return (start_voltage/(start_voltage-end_voltage))*amphours #Not sure how accurate this is but it should be close enough for us

class Battery:
    def __init__(self,voltage,amphours):
        self.normal_amphours = amphours
        self.amphours = amphours
        self.voltage = voltage
        self.normal_voltage = voltage

    def SetCharge(self,percent):
        self.amphours = self.normal_amphours*(percent/100)

    def calculate(self):

        amps = 1000 #This should work for negative numbers, which is effectively charging the battery.

        amp_hours_used = (amps*0.1) #Delta time.

        amp_hours_used = (amps/3600) #To hours

        self.amphours = self.amphours-amp_hours_used

        self.voltage = (self.amphours/self.normal_amphours)*self.normal_voltage

Batt = Battery(130,findAmpHoursToZero())

i = 0
import time

import matplotlib.pyplot as plt

class Transient:
    def __init__(self,name):
        self.graphs = {}
        self.shown = False
        self.name = name

    def add_graph(self,name):
        x = self.graphs.copy()
        x[name] = []
        y = x
        self.graphs = y

    def add(self,name,value):
        self.graphs[name].append(value)

    def generate_plot(self):
        if self.shown: return
        self.shown = True

        fig, ax = plt.subplots()
        ax.set_title(self.name)
        
        for plot_name in self.graphs:
            plot = self.graphs[plot_name]

            ax.plot(plot,label=plot_name)

        ax.legend()
            
            
        plt.show()

t = Transient("Battery 15A draw")

t.add_graph("Voltage")

while i < 500:
    i+=1
    Batt.calculate()
    t.add("Voltage",round(Batt.voltage,4))
    time.sleep(0.01)

t.generate_plot()