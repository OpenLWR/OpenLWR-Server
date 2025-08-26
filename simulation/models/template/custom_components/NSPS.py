from enum import Enum
class BWR6ScramTrips(Enum):
    MANUAL = 1
    MODESWITCH = 2
    LEVELLOW = 3
    REACPRESSHIGH = 4

class NuclearSystemProtectionSystem:
    def __init__(self,Divisions=[]):
        self.scram = False
        assert len(Divisions) == 4, "NSPS Must have four divisions"
        self.RPSDivs = Divisions

    def run(self):
        if (self.RPSDivs[0].Tripped and self.RPSDivs[3].Tripped) or (self.RPSDivs[1].Tripped and self.RPSDivs[2].Tripped):
            self.scram = True #TODO: De-energize individual HCU groups

        ScramTrips = []
        for Div in self.RPSDivs:
            for Scram in Div.Trips:
                ScramTrips.append(Scram)

        for Div in self.RPSDivs:
            Div.AllTrips = ScramTrips
            Div.run()
        
class NSPSDivision:
    def __init__(self):
        self.Trips = [] #Just because theres a trip in doesnt mean the division is actually in trip!
        self.AllTrips = [] #Received from the NSPS
        self.Tripped = False

    def trip(self,trip_type):
        if not trip_type in self.Trips:
            self.Trips.append(trip_type)

    def run(self):
        for ScramTrip in BWR6ScramTrips:
            if self.AllTrips.count(ScramTrip) >= 2:
                self.Tripped = True #2 of 4 voter trips
        