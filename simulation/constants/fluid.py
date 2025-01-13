import math

class LiquidHeader:
    def __init__(self,fill,normal_pressure,diameter,length=2000):
        """diameter and length in mm"""
        self.fill = fill
        self.normal_pressure = normal_pressure #PSIG
        self.feeders = []

        volume = diameter / 2
        volume = math.pi * (volume ** 2)
        volume = volume * length
        volume = volume / 1e6  # convert liters

        self.liters_at_full = volume

    def add_feeder(self,header,valve=None):
        self.feeders.append({"header":header,"valve":valve})

    def get_pressure(self):
        return self.fill * self.normal_pressure

    def calculate(self):
        Press = self.fill * self.normal_pressure