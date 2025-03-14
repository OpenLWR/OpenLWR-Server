from simulation.constants.electrical_types import ElectricalType
from simulation.constants.equipment_states import EquipmentStates
from simulation.models.control_room_columbia.general_physics import ac_power
from simulation.models.control_room_columbia.general_physics import air_system
from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.libraries import pid
import math
import log

class DieselGenerator():
    def __init__(self,name,cs = "",output = "",auto = False,loca = False,lockout = False,voltage = 0,frequency = 0,annunciators={},inertia = 0,horsepower = 0,sa_valve=None,sa_header=None):
        self.name = name
        self.dg = {
            "state" : EquipmentStates.STOPPED,
            "control_switch" : cs,
            "output_breaker" : output,
            "rpm" : 0, #normal is 900
            "rpm_set" : 900,
            "throttle" : 0,
            "volt_reg" : 1,
            "current" : 0,
            "field_voltage" : 0,
            "angular_velocity" : 0,
            "auto_start" : auto,
            "loca_start" : loca,
            "lockout" : lockout,
            #TODO: voltage regulator/rpm governor
            "voltage" : voltage,
            "frequency" : frequency, #8 pole generator. 60hz@900rpm
            "annunciators" : annunciators,
            "time" : 0,

            "sa_valve" : sa_valve,
            "sa_header" : sa_header,
        }
        self.physics_constants = {
            "horsepower" : horsepower,
            "inertia" : inertia,
        }
        self.governor_pid = pid.PIDExperimental(0.013,0.002,0.001,0,1) #pid.PID(0.25,0.001,0.01,-0.2,0.2)
        self.volt_reg_pid = pid.PIDExperimental(0.0001,0.001,0,0,2)

    def can_start(self):
        """Returns true if the DG is not locked out, or starting already"""
        return not self.dg["lockout"] and self.dg["state"] == EquipmentStates.STOPPED

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
                self.stop()

            if cont_sw["position"] == 2:
                #TODO: flag position autostart alarm clear (and running alarm?)
                self.start()

            if "green" in cont_sw["lights"]:
                cont_sw["lights"]["green"] = self.dg["rpm"] < 150
                cont_sw["lights"]["red"] = self.dg["rpm"] >= 150

            if "cranking" in cont_sw["lights"]:
                cont_sw["lights"]["cranking"] = self.dg["sa_valve"].percent_open > 0

    def set_annunciator(self,name,alarmed):
        if name in self.dg["annunciators"]:
            model.alarms[self.dg["annunciators"][name]]["alarm"] = alarmed

    def calculate(self):
        #huge thanks to @fluff.goose (discord) for help with this
        throttle = self.dg["throttle"]

        if self.dg["state"] == EquipmentStates.STARTING:
            self.dg["time"] += 0.1 

        if self.dg["rpm"] > 150 and self.dg["state"] == EquipmentStates.STARTING:
            self.dg["state"] = EquipmentStates.RUNNING
            self.dg["time"] = 0

        if self.dg["rpm"] <= 150 and self.dg["state"] == EquipmentStates.STARTING:

            if self.dg["time"] >= 10: #Incomplete Sequence (K4 Relay)
                self.dg["lockout"] = True
                self.dg["time"] = 0
                self.set_annunciator("INCOMPLETESEQUENCE",True)

            self.dg["sa_valve"].stroke_open()

            self.dg["throttle"] = 0 #the start air motors are increasing speed

        elif self.dg["rpm"] >= 150 or self.dg["state"] != EquipmentStates.STARTING:
            self.dg["sa_valve"].stroke_closed()

        if self.dg["lockout"]:
            self.dg["state"] = EquipmentStates.STOPPING

        self.set_annunciator("LOCKOUT",self.dg["lockout"])
        self.set_annunciator("AUTOSTART",self.dg["auto_start"])

        starter_torque = (200*5252)/900

        start_air = max(min((self.dg["sa_header"].get_pressure()-100)/100,1),0)

        starter_torque = starter_torque*start_air*(self.dg["sa_valve"].percent_open/100)

        horsepower = self.physics_constants["horsepower"]

        torque = (horsepower*5252)/900

        torque = torque*throttle

        total_load = 0

        for load in ac_power.sources[self.name].info["loads"]:
            total_load += ac_power.sources[self.name].info["loads"][load]

        generator_load = total_load

        generator_torque = ((generator_load/746)*5252)/900 #746 watts is 1 horsepwer

        generator_omega = generator_torque/self.physics_constants["inertia"] #slows down the engine when its loaded

        omega = (torque+starter_torque)/self.physics_constants["inertia"]

        omega -= (self.dg["angular_velocity"]*0.003)

        self.dg["angular_velocity"] = self.dg["angular_velocity"]+((omega-generator_omega)*10) #rad/s

        self.dg["angular_velocity"] = max(self.dg["angular_velocity"],0)

        self.dg["rpm"] = self.dg["angular_velocity"]*60/(2*math.pi) 

        if self.dg["rpm"] <= 50 and self.dg["state"] == EquipmentStates.STOPPING:
            self.dg["state"] = EquipmentStates.STOPPED
            self.dg["angular_velocity"] = 0

        self.dg["frequency"] = 60*(self.dg["rpm"]/900)


        if self.dg["state"] == EquipmentStates.RUNNING:
            volts = 4160*(self.dg["volt_reg"])
            volt_drop = 0.2*((generator_load/(volts+0.1)))
            volts = volts-volt_drop
            self.dg["voltage"] = volts
        else:
            self.dg["voltage"] = 0

        self.dg["current"] = generator_load/(self.dg["voltage"]+0.1)
        ac_power.sources[self.name].info["voltage"] = self.dg["voltage"]
        ac_power.sources[self.name].info["frequency"] = self.dg["frequency"]

        


    def governor(self):
        pid_output = self.governor_pid.update(self.dg["rpm_set"],self.dg["rpm"],0.1)

        self.dg["throttle"] = pid_output

        if self.dg["state"] == EquipmentStates.STOPPED:
            self.governor_pid.reset()

        if self.dg["state"] == EquipmentStates.STOPPED or self.dg["state"] == EquipmentStates.STOPPING:
            self.dg["throttle"] = 0

    def volt_reg(self):
        #The voltage regulator controls the Exciter
        #https://www.nrc.gov/docs/ML1122/ML11229A143.pdf

        if self.dg["state"] != EquipmentStates.RUNNING:
            self.volt_reg_pid.reset()
            self.dg["volt_reg"] = 0

        pid_output = self.volt_reg_pid.update(4160,self.dg["voltage"],0.1) #TODO: Voltage Regulator adjust

        self.dg["volt_reg"] = pid_output




dg1 = None
dg2 = None
dg3 = None

DSA_AR_1A = None #DIESEL STARTING AIR RECEIVER SKID DSA-AR-1A
DSA_AR_1B = None #DIESEL STARTING AIR RECEIVER SKID DSA-AR-1B
DSA_AR_1C = None #Simplified. There is two independent air receivers for HPCS.

DSA_PCV_2A = None #SA Pressure control valves
DSA_PCV_2B = None
DSA_PCV_2C = None

DSA_V_17A = None #This is the Clinton valve. Simplified. There is two, DSA-V-11A and 17A. Div 1 DG.
DSA_V_17B = None #This is the Clinton valve. Simplified. There is two, DSA-V-11B and 17B. Div 2 DG.
DSA_V_4 = None #This is the Clinton valve. Also simplified. there is two. HPCS DG.

DSA_DG1 = None #Local Start Air Pressure
DSA_DG2 = None
DSA_DG3 = None 

DSA_V_3A1 = None
DSA_V_3B1 = None
DSA_V_3C1 = None #Simplified. There is two valves, one per pair of start motors. Supplies air to the start air motors.

ATMOSPHERE = None

def initialize():
    global dg1
    global dg2
    global dg3

    global DSA_AR_1A
    global DSA_AR_1B 
    global DSA_AR_1C

    global DSA_PCV_2A
    global DSA_PCV_2B
    global DSA_PCV_2C

    global DSA_V_17A
    global DSA_V_17B
    global DSA_V_4

    global DSA_DG1
    global DSA_DG2
    global DSA_DG3

    global DSA_V_3A1
    global DSA_V_3B1
    global DSA_V_3C1

    global ATMOSPHERE

    DSA_AR_1A = air_system.AirHeader(1,250,25)
    DSA_AR_1B = air_system.AirHeader(1,250,25)
    DSA_AR_1C = air_system.AirHeader(1,250,15)

    #Start Air Isolation Valves
    DSA_V_17A = air_system.Valve(100,open_speed=50)
    DSA_V_17B = air_system.Valve(100,open_speed=50)
    DSA_V_4 = air_system.Valve(100,open_speed=50)

    #Start air lines after isol valves

    DSA_DG1 = air_system.AirHeader(1,225,1)
    DSA_DG2 = air_system.AirHeader(1,225,1)
    DSA_DG3 = air_system.AirHeader(1,225,1)

    #Start Air pressure control valves
    DSA_PCV_2A = air_system.PressureControlValve(100,DSA_DG1,225)
    DSA_PCV_2B = air_system.PressureControlValve(100,DSA_DG2,225)
    DSA_PCV_2C = air_system.PressureControlValve(100,DSA_DG3,225)

    DSA_V_3A1 = air_system.Valve(0,open_speed=100)
    DSA_V_3B1 = air_system.Valve(0,open_speed=100)
    DSA_V_3C1 = air_system.Valve(0,open_speed=100)

    ATMOSPHERE = air_system.Vent()

    DSA_DG1.add_feeder(DSA_AR_1A,DSA_PCV_2A,DSA_V_17A)
    DSA_DG2.add_feeder(DSA_AR_1B,DSA_PCV_2B,DSA_V_17B)
    DSA_DG3.add_feeder(DSA_AR_1C,DSA_PCV_2C,DSA_V_4)

    ATMOSPHERE.add_feeder(DSA_DG1,DSA_V_3A1)
    ATMOSPHERE.add_feeder(DSA_DG2,DSA_V_3B1)
    ATMOSPHERE.add_feeder(DSA_DG3,DSA_V_3C1)


    dg1 = DieselGenerator("DG1",cs = "diesel_gen_1",output = "cb_dg1_7",inertia=36000,horsepower=6000,sa_valve=DSA_V_3A1,sa_header=DSA_DG1,
                          annunciators={}
                          )
    dg2 = DieselGenerator("DG2",cs = "diesel_gen_2",output = "cb_dg2_8",inertia=36000,horsepower=6000,sa_valve=DSA_V_3B1,sa_header=DSA_DG2,
                          annunciators={"INCOMPLETESEQUENCE" : "dg_2_fail_to_start",
                                        "LOCKOUT" : "dg_2_lockout",
                                        "AUTOSTART" : "dg_2_autostart",
                                        "IMPROPERPARALLELING" : "dg_2_improper_parallel",
                                        }
                          )
    dg3 = DieselGenerator("DG3",cs = "diesel_gen_3",output = "cb_dg3_4",inertia=36000,horsepower=6000,sa_valve=DSA_V_3C1,sa_header=DSA_DG3)

def run():
    DSA_AR_1A.calculate()
    DSA_AR_1B.calculate()
    DSA_AR_1C.calculate()

    DSA_DG1.calculate()
    DSA_DG2.calculate()
    DSA_DG3.calculate()

    ATMOSPHERE.calculate()


    dg1.check_controls()
    dg1.calculate()
    dg1.governor()
    dg1.volt_reg()

    model.values["dg1p1volts"] = dg1.dg["voltage"]
    model.values["dg1p2volts"] = dg1.dg["voltage"]
    model.values["dg1p3volts"] = dg1.dg["voltage"]
    model.values["dg1_freq"] = dg1.dg["frequency"]
    model.values["dg1p1amps"] = dg1.dg["current"]
    model.values["dg1p2amps"] = dg1.dg["current"]
    model.values["dg1p3amps"] = dg1.dg["current"]

    dg2.check_controls()
    dg2.calculate()
    dg2.governor()
    dg2.volt_reg()

    model.values["dg2p1volts"] = dg2.dg["voltage"]
    model.values["dg2p2volts"] = dg2.dg["voltage"]
    model.values["dg2p3volts"] = dg2.dg["voltage"]
    model.values["dg2_freq"] = dg2.dg["frequency"]
    model.values["dg2p1amps"] = dg2.dg["current"]
    model.values["dg2p2amps"] = dg2.dg["current"]
    model.values["dg2p3amps"] = dg2.dg["current"]

    dg3.check_controls()
    dg3.calculate()
    dg3.governor()
    dg3.volt_reg()
