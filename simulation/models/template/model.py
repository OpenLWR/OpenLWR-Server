from simulation.models.template.states.NSPS import State as NSPSState
from simulation.models.template.custom_components.NSPS import BWR6ScramTrips

class Model:
    def __init__(self):
        # do what you need to do here to get your model ready
        self.NSPSState = NSPSState()
        self.replicated_data = {}

    # check __init__.py for setting how often these run
    def step(self, delta):
        #TODO: find out if we want to leave this here or where we want this to go
        self.NSPSState.NSPS.run()
        print(self.NSPSState.NSPS.scram, self.NSPSState.Div1.Tripped,self.NSPSState.Div2.Tripped,self.NSPSState.Div3.Tripped,self.NSPSState.Div4.Tripped)

    def step_slow(self, delta):
        print("Hello, World! but slower")

        if BWR6ScramTrips.LEVELLOW in self.NSPSState.Div1.Trips: #Tripping the second division which initiates a reactor scram
            self.NSPSState.Div2.trip(BWR6ScramTrips.LEVELLOW)

        self.NSPSState.Div1.trip(BWR6ScramTrips.LEVELLOW) #Testing to see if one trip will cause a scram