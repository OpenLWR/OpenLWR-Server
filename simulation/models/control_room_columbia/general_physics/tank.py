import math

def calculate_level_cylinder(Height,Volume,MassOfLiquid):
    #calculate the volume of the cylinder
    #piR^2
    VolumeOfLiquid = MassOfLiquid*1000000 #to mm^3

    #Because this uses volume, we can simulate water expansion.
    return ((VolumeOfLiquid/Volume)*Height) #outputs in mm

def mm_to_inches(value):
    return value/25.4

def ft_to_mm(value):
    return value*304.8

class TankCylinder:
    def __init__(self,name,diameter,height,kg):
        """measurements should be in mm"""
        self.name = name

        self.diameter = diameter
        self.radius = diameter/2
        self.height = height

        self.volume = math.pi * (self.radius**2) * self.height #mm^3
        self.contents_kg = kg

        self.level = 0

        tanks[self.name] = self

    def get_level(self):

        level = calculate_level_cylinder(self.height,self.volume,self.contents_kg)

        self.level = level
        return level
    
    def add_water(self,amount):
        self.contents_kg += amount

tanks = {}

#wetwell 
TankCylinder("Wetwell",ft_to_mm(87),ft_to_mm(67),3785411.7840007) # 1 million gallons, not sure if its even close to correct