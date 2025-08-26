from simulation.models.template.custom_components.NSPS import NSPSDivision,NuclearSystemProtectionSystem

class State:
    def __init__(self):
        self.Div1 = NSPSDivision()
        self.Div2 = NSPSDivision()
        self.Div3 = NSPSDivision()
        self.Div4 = NSPSDivision()

        self.NSPS = NuclearSystemProtectionSystem([self.Div1,self.Div2,self.Div3,self.Div4])

