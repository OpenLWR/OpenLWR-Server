
class SLC():
    def __init__(self,uid):
        self.uid = uid
        self.ground = False
        self.trouble = False
        self.fire = False
        self.areas = []

    def add_detector(self,area_name):
        if area_name not in self.areas:
            self.areas[area_name] = False #Allows proper annunciation of "general area" and whatnot

    def detector_triggered(self,area_name):
        self.fire = True
        self.areas[area_name] = True

    def detector_untriggered(self,area_name):
        self.areas[area_name] = False

class Detector_Type_Photo:
    def __init__(self,uid,slc,area):
        self.uid = uid
        self.sensitivity = 3 #percent of smoke in the area
        self.slc = slc #SLC loop it is attatched to
        self.area = area

        slc.add_detector(self.area.name)

    def heartbeat(self):
        area_temperature = self.area.temperature
        area_smoke = self.area.smoke_content

        if area_smoke > self.sensitivity:
            #go into alarm
            self.slc.detector_triggered(self.area.name)
        else:
            self.slc.detector_untriggered(self.area.name)



class Area:
    def __init__(self,name,volume):
        self.name = name
        self.volume = volume
        self.temperature = 60
        self.smoke_content = 0 #perecent
        self.fires = []
        self.suppression = None #A area can only have one suppression device


class Fire_Type_Paper: #Easy to extinguish, moderate smoke
    def __init__(self,area_name,intensity):
        self.intensity = intensity
        self.area = area_name
        self.spread_chance = 0 #Goes up over time as the fire is not extinguished.

    def spread_to_areas(self):
        print("Spread")

    def calculate(self):
        heat_generation = self.intensity*20
        


