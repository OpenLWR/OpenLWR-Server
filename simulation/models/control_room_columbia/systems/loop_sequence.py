from simulation.models.control_room_columbia.general_physics import ac_power
from simulation.models.control_room_columbia import model

class Sequence():

    def __init__(self,bus_name):
        self.bus_name = bus_name
        self.loads = {}
        self.sequence_enabled = False #Occurs on a Loss Of Power
        self.sequence_timer = -1
        self.highest_time = 0

        sequences[bus_name] = self

    def add_pump(self,name,time):
        """Adds a pump to be sequenced on, in seconds"""
        time = time*10
        self.loads[name] = time

        self.highest_time = max(self.highest_time,time)

        model.pumps[name]["loop_seq"] = True

    def calculate(self):

        no_voltage = not ac_power.busses[self.bus_name].is_voltage_at_bus(120) #at LEAST 120 volts at the bus

        if no_voltage:
            self.sequence_enabled = True
            self.sequence_timer = -1

        if not no_voltage and self.sequence_enabled:
            if self.sequence_timer == -1:
                self.sequence_timer = 0
            elif self.sequence_timer < self.highest_time:
                self.sequence_timer += 1
            else:
                self.sequence_timer = -1
                self.sequence_enabled = False
            
        for load in self.loads:
            model.pumps[load]["loop_avail"] = self.sequence_timer >= self.loads[load] or not self.sequence_enabled
            

        



sequences = {}

def initialize():
    Sequence("7")
    sequences["7"].add_pump("lpcs_p_1",0)
    sequences["7"].add_pump("rhr_p_2a",5)

    Sequence("8")
    sequences["8"].add_pump("rhr_p_2c",0)
    sequences["8"].add_pump("rhr_p_2b",5)

def run():
    for sequence in sequences:
        sequence = sequences[sequence]
        sequence.calculate()