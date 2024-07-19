from simulation.constants.electrical_types import ElectricalType
from simulation.constants.equipment_states import EquipmentStates
from simulation.models.control_room_columbia.general_physics import ac_power
from simulation.models.control_room_columbia import model

class DieselGenerator():
    def __init__(self,name,cs = "",output = "",rpm = 0,sa = 500,auto = False,loca = False,trip = False,lockout = False,voltage = 0,frequency = 0,annunciators={}):
        self.name = name
        self.dg = {
            "state" : EquipmentStates.STOPPED,
            "control_switch" : cs,
            "output_breaker" : output,
            "rpm" : rpm, #normal is 900
            "start_air_press" : sa,
            "auto_start" : auto,
            "loca_start" : loca,
            "trip" : trip,
            "lockout" : lockout,
            #TODO: voltage regulator/rpm governor
            "voltage" : voltage,
            "frequency" : frequency, #8 pole generator. 60hz@900rpm
            "annunciators" : annunciators
        }

    def can_start(self):
        """Returns true if the DG is not tripped,locked out, or starting already"""
        return not self.dg["lockout"] and not self.dg["trip"] and self.dg["state"] == EquipmentStates.STOPPED

    def start(self,auto = False):
        """Starts the diesel generator"""
        if self.can_start():
            self.dg["state"] = EquipmentStates.STARTING
            if auto:
                self.dg["auto_start"] = True

    def can_stop(self):
        """Returns true if the DG is able to be stopped normally."""
        return self.dg["state"] == EquipmentStates.RUNNING
    
    def stop(self):
        """Stops the diesel generator normally."""
        if self.can_stop():
            self.dg["state"] == EquipmentStates.STOPPING
            self.dg["auto_start"] = False

    def check_controls(self):
        """Default start/stop control switch for the diesel generator.
        This does NOT have to be used, you can use start(), and stop()"""
        if self.dg["control_switch"] in model.switches:
            cont_sw = model.switches[self.dg["control_switch"]]

            if cont_sw["position"] == 0:
                #a loca autostart prevents this?
                if self.dg["state"] == EquipmentStates.RUNNING:
                    self.dg["state"] = EquipmentStates.STOPPING

            if cont_sw["position"] == 2:
                #TODO: flag position autostart alarm clear (and running alarm?)
                if self.dg["state"] == EquipmentStates.STOPPED:
                    self.dg["state"] = EquipmentStates.STARTING

            if "green" in cont_sw["lights"]:
                cont_sw["lights"]["green"] = self.dg["state"] == EquipmentStates.STOPPED
                cont_sw["lights"]["red"] = self.dg["state"] != EquipmentStates.STOPPED

    def calculate(self):
        match self.dg["state"]:
            case EquipmentStates.STARTING:
                self.dg["rpm"] += 7.5
                #TODO: actual start air press
                self.dg["start_air_press"] = 100 #Start air alarms at 238 psig, compressor starts at 241 psig
                if self.dg["rpm"] >= 900:
                    #TODO: Dont close output breaker if bus is not UV'd
                    if self.dg["auto_start"] and not self.dg["loca_start"]:
                        ac_power.close_breaker(self.dg["output_breaker"])
                    self.dg["state"] = EquipmentStates.RUNNING
                    self.dg["rpm"] = 900

                self.dg["frequency"] = (self.dg["rpm"]*8)/120 
                self.dg["voltage"] = (self.dg["rpm"]/900)*4160 #TODO: realistic voltage
            
            case EquipmentStates.RUNNING:
                self.dg["start_air_press"] = 500
                self.dg["frequency"] = (self.dg["rpm"]*8)/120 
                self.dg["voltage"] = (self.dg["rpm"]/900)*4160 #TODO: realistic voltage

            case EquipmentStates.STOPPING:
                self.dg["start_air_press"] = 500
                self.dg["rpm"] -= 7.5
                if self.dg["rpm"] <= 0:
                    self.dg["state"] = EquipmentStates.STOPPED
                    self.dg["rpm"] = 0

                self.dg["frequency"] = (self.dg["rpm"]*8)/120 
                self.dg["voltage"] = (self.dg["rpm"]/900)*4160 #TODO: realistic voltage
                    
            case EquipmentStates.STOPPED:
                self.dg["frequency"] = 0
                self.dg["voltage"] = 0

        if self.name in ac_power.sources:
            ac_power.sources[self.name]["voltage"] = self.dg["voltage"]
            ac_power.sources[self.name]["frequency"] = self.dg["frequency"]

dg1 = None
dg2 = None
dg3 = None

def initialize():
    global dg1
    global dg2
    global dg3
    dg1 = DieselGenerator("DG1",cs = "diesel_gen_1",output = "cb_dg1_7")
    dg2 = DieselGenerator("DG2",cs = "diesel_gen_2",output = "cb_dg2_8")
    #dg3 = DieselGenerator("DG3",cs = "",output = "")

def run():
    dg1.calculate()
    dg1.check_controls()
    dg2.calculate()
    dg2.check_controls()