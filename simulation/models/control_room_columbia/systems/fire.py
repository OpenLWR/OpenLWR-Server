from simulation.models.control_room_columbia.general_physics import ac_power
import random

def DamageEquipmentTGElect471(fire_time):
    breakers_allowed = ["cb_s1","cb_s2","cb_s3"]
    if fire_time > 100:
        for breaker_name in ac_power.breakers:
            if breaker_name in breakers_allowed:
                if random.randint(0,2000) == 4:
                    ac_power.breakers[breaker_name].info["lockout"] = True
                    ac_power.breakers[breaker_name].open()

class SLC():
    def __init__(self,uid):
        self.uid = uid
        self.ground = False
        self.trouble = False
        self.fire = False
        self.areas = {}

        SLCs[self.uid] = self

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

        detectors.append(self)

    def heartbeat(self):
        area_temperature = self.area.temperature
        area_smoke = self.area.smoke_content

        if area_smoke > self.sensitivity:
            #go into alarm
            self.slc.detector_triggered(self.area.name)
        else:
            self.slc.detector_untriggered(self.area.name)

class Suppression_Type_Wet:
    def __init__(self,uid,slc,area,head_shatter,head_flowrate):
        self.uid = uid
        self.slc = slc
        self.area = area
        self.head_shatter = head_shatter
        self.head_flowrate = head_flowrate
        self.shattered = False

        self.slc.add_detector(self.area.name+"_FLOW")

        suppression[self.uid] = self

    def heartbeat(self):
        area_temperature = self.area.temperature

        if area_temperature > self.head_shatter:
            self.shattered = True

        if self.shattered:
            self.slc.detector_triggered(self.area.name+"_FLOW")
            #begin suppression flow

            #TODO:use actual flow calculations
            pressure = 100 #TODO
            flow = self.head_flowrate * (pressure/100)

            #TODO: add fire header

            effectiveness = flow/111

            for fire in self.area.fires:
                fire.suppress(effectiveness)
                



class Area:
    def __init__(self,name,volume):
        self.name = name
        self.volume = volume
        self.temperature = 20
        self.smoke_content = 0 #perecent
        self.fires = []
        self.suppression = None #A area can only have one suppression device
        self.equipment = []

        areas[name] = self

    def add_equipment(self,func):
        self.equipment.append(func)


class Fire_Type_Paper: #Easy to extinguish, moderate smoke
    def __init__(self,area,intensity):
        self.set_intensity = intensity
        self.intensity = intensity #TODO: Make this come up to set_intensity over time
        self.area = area
        self.spread_chance = 0 #Goes up over time as the fire is not extinguished.
        self.put_out_effectiveness = 0.05 #very easy to extinguish
        self.fire_time = 0 #seconds

        fires.append(self)
        self.area.fires.append(self)

    def spread_to_areas(self):
        print("Spread")

    def put_out(self):
        self.area.fires.remove(self)
        fires.remove(self)
        print("%s fire is out." % self.area.name)

    def suppress(self,effectiveness):
        suppression = effectiveness/self.put_out_effectiveness

        if suppression > 1:
            self.put_out()
        else:
            self.intensity -= self.intensity*suppression*0.01
            self.intensity = max(self.intensity,0.1)
            self.put_out_effectiveness = self.intensity*0.95

    def calculate(self,delta):
        self.fire_time += delta
        heat = 180*(self.intensity+0.15)
        self.area.temperature += (heat-self.area.temperature)*0.01
        self.area.smoke_content += 0.1*self.intensity
        
        self.area.smoke_content = min(max(self.area.smoke_content,0),100)

        for equip in self.area.equipment:
            equip(self.fire_time)

class Fire_Type_Electrical: #Hard to extinguish, moderate smoke, requires de-energization(?)
    def __init__(self,area,intensity):
        self.set_intensity = intensity
        self.intensity = intensity #TODO: Make this come up to set_intensity over time
        self.area = area
        self.spread_chance = 0 #Goes up over time as the fire is not extinguished.
        self.put_out_effectiveness = 0.7
        self.fire_time = 0 #seconds

        fires.append(self)
        self.area.fires.append(self)

    def spread_to_areas(self):
        print("Spread")

    def put_out(self):
        self.area.fires.remove(self)
        fires.remove(self)
        print("%s fire is out." % self.area.name)

    def suppress(self,effectiveness):
        suppression = effectiveness/self.put_out_effectiveness

        if suppression > 1:
            self.put_out()
        else:
            self.intensity -= self.intensity*suppression*0.01
            self.intensity = max(self.intensity,0.2)
            self.put_out_effectiveness = self.intensity*0.95

    def calculate(self,delta):
        self.fire_time += delta
        heat = 200*(self.intensity+0.15)
        self.area.temperature += (heat-self.area.temperature)*0.01
        self.area.smoke_content += 0.1*self.intensity
        
        self.area.smoke_content = min(max(self.area.smoke_content,0),100)
        
        for equip in self.area.equipment:
            equip(self.fire_time)

detectors = []
fires = []
SLCs = {}
areas = {}
suppression = {}

def initialize():
    tg = Area("TG BLDG 471 ELECT SWGR",100)
    tg.add_equipment(DamageEquipmentTGElect471)
    tgslc = SLC("TG BLDG 471 ELECT SWGR")
    tgslcsp = SLC("SYS 7 WET PIPE TG BLDG 471 ELECT SWGR")
    Detector_Type_Photo("PHOTO TG 471", tgslc,tg)
    Suppression_Type_Wet("SYS 7 WET PIPE TG BLDG 471 ELECT SWGR",tgslcsp,tg,93,11)
    #Fire_Type_Electrical(tg,0.4)

def run(delta):
    for detector in detectors:
        detector.heartbeat()

    for system in suppression:
        system = suppression[system]
        system.heartbeat()

    for fire in fires:
        fire.calculate(delta)