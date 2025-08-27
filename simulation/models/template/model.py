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
        print(self.NSPSState.NSPS.scram)

    def step_slow(self, delta):
        print("Hello, World! but slower")