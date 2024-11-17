from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory

#Engineered Safeguard Feature Actuation System

RPV_LEVEL_1_in = -129
RPV_LEVEL_2_in = -51
RPV_LEVEL_3_in = 13
RPV_LEVEL_4_in = 31.5 #From Columbia Notes
RPV_LEVEL_8_in = 54

PSIG_TO_PASCAL = 6895

# follow up on this value
# using the midpoint from ITS LCO 3.3.5.1 table 4.d/4.c looks about right
ADS_RHR_PRESS_PERMISSIVE_PSIG = 125
ADS_RHR_PRESS_PERMISSIVE_PA = ADS_RHR_PRESS_PERMISSIVE_PSIG * PSIG_TO_PASCAL
ADS_LPCS_PRESS_PERMISSIVE_PSIG = 145
ADS_LPCS_PRESS_PERMISSIVE_PA = ADS_LPCS_PRESS_PERMISSIVE_PSIG * PSIG_TO_PASCAL
ADS_DELAY_TIMER_sec = 105

HIGH_DRYWELL_PRESS_PSIG = 1.68
HIGH_DRYWELL_PRESS_PA = HIGH_DRYWELL_PRESS_PSIG * PSIG_TO_PASCAL

RPS_APRM_HI_FLUX_TRIP = 118 #Percent
RPS_APRM_FLOW_TRIP_CLAMP = 113.5 #Percent 
RPS_APRM_SETDOWN_TRIP = 15 # Percent
RPS_HI_RPV_PRESSURE = 1060 #PSIG
RPS_HI_DW_TRIP = 1.68 #PSIG
RPS_IRM_TRIP = 120 #Scale
RPS_TSV_TRIP_POS = 95 #Percent
RPS_TCV_PRESS_TRIP = 1250 #PSIG
RPS_TURB_TRIP_BYP = 30 #% Power

ATWS_HIGH_PRESSURE = 1120 * PSIG_TO_PASCAL

RATED_CORE_FLOW_LB_HR = 108.5e6

class ADS_Logic:
    
    def __init__(self, train):
        self.ADS_INITIATED_1 = False
        self.ADS_INITIATED_2 = False
        self.ADS_SYS_INITIATED = False
        self.ADS_INHIBIT = False
        self.ADS_Timer_Sec = 0
        self.ADS_Timer_Status = False
        self.sw_init_1 = "ads_initiate_" + train + "a"
        self.sw_init_2 = "ads_initiate_" + train + "b"
        self.sw_inhib = "ads_inhibit_" + train
        self.sw_reset = "ads_reset_" + train
        self.Train = train

    def ADS_Run(self,LevelNR_in, LevelWR_in, RHR_A_PRESS, RHR_B_PRESS, RHR_C_PRESS, LPCS_PRESS, delta):

        #TODO: Check power available. If not available, timer stop and return

        #Switches:
        self.ADS_INHIBIT_CHECK(model.switches[self.sw_inhib]["position"])
        if(model.buttons[self.sw_init_1]["state"] == True) : {
            self.ADS_INITIATE_1()
        }
        if(model.buttons[self.sw_init_2]["state"] == True) : {
            self.ADS_INITIATE_2()
        }
        if(model.buttons[self.sw_reset]["state"] == True) : {
            self.ADS_RESET_LOGIC()
        }

        #Logic:
        
        if self.ADS_Timer_Status == False:
            self.ADS_Timer_Start()

        if LevelNR_in > RPV_LEVEL_3_in or LevelWR_in > RPV_LEVEL_1_in:
            self.ADS_Timer_Stop()

        if self.ADS_Timer_Run(delta) == False:
            return


        if self.Train == "1":
            if RHR_A_PRESS > ADS_RHR_PRESS_PERMISSIVE_PSIG or LPCS_PRESS > ADS_LPCS_PRESS_PERMISSIVE_PSIG:
                if self.ADS_INHIBIT == False:
                    self.ADS_INITIATE_1()
                    self.ADS_INITIATE_2()
        
        if self.Train == "2":
            if RHR_B_PRESS > ADS_RHR_PRESS_PERMISSIVE_PSIG or RHR_C_PRESS > ADS_RHR_PRESS_PERMISSIVE_PSIG:
                if self.ADS_INHIBIT == False:
                    self.ADS_INITIATE_1()
                    self.ADS_INITIATE_2()


    def ADS_INITIATE_1(self):
        self.ADS_INITIATED_1 == True
        if self.ADS_INITIATED_2 == True:
            self.ADS_SYS_INITIATED = True

    def ADS_INITIATE_2(self):
        self.ADS_INITIATED_2 = True
        if self.ADS_INITIATED_1 == True:
            self.ADS_SYS_INITIATED = True
       
    def ADS_RESET_LOGIC(self):
        self.ADS_INITIATED_1 = False
        self.ADS_INITIATED_2 = False
        self.ADS_SYS_INITIATED = False
        self.ADS_Timer_Sec = 0

    def ADS_INHIBIT_CHECK(self, Inhibit_Sw):
        if Inhibit_Sw == False:
            self.ADS_INHIBIT = False
        elif self.ADS_INHIBIT == False:
            self.ADS_INHIBIT = True
         

    def ADS_Timer_Run(self, delta):
        #TODO: check power. If power is lost, set status to false and time to 0
        if self.ADS_Timer_Status == False:
            return False 
        if self.ADS_Timer_Status == True:
            self.ADS_Timer_Sec += delta 
        if self.ADS_Timer_Sec > ADS_DELAY_TIMER_sec:
            return True
        return False

    def ADS_Timer_Start(self):
        self.ADS_Timer_Status = True

    def ADS_Timer_Stop(self):
        self.ADS_Timer_Status = False   
        self.ADS_Timer_Sec = 0


#RPS Logic not yet implemented. Work in progress
#See TODOs prior to implementation
class RPS_Logic:

    RPS_SYS_INIT = False
    RPS_Trip_Ch = {
        "A1" : False,
        "A2" : False,
        "B1" : False,
        "B2" : False,
    }

    def __init__(self,TrainChannel):
        self.Train = TrainChannel
        self.ModeSwTimer = 0
        self.RPS_Trip_In = False
        self.High_Dw_Press = EventHandler() #TOOD: Integrate into the RPS_RUN


#units for RPS:
#LevelNR is in inches
# aprm flux is in % flux of rated
#core flow is in % of rated core flow
#RPV Press, DW Press, are in PSIG

    def RPS_RUN(self, delta, LevelNR, APRMFlux, CoreFlow, OPRMTrip, IRMs, RPVPress, DWPress, TSVPos, EHCPress, MSIVPos, ModeSw,ManScram):

        if RPS_Logic.RPS_SYS_INIT:
            return
        
        RpsTripSignal = False

        if LevelNR < RPV_LEVEL_3_in:
            RpsTripSignal = True 

        if ModeSw == model.ReactorMode.RUN:
            if APRMFlux > RPS_APRM_HI_FLUX_TRIP or APRMFlux > RPS_APRM_FLOW_TRIP_CLAMP:
                RpsTripSignal = True
            ThermalTrip = .58 * CoreFlow + .59
            if ThermalTrip > RPS_APRM_FLOW_TRIP_CLAMP:
                ThermalTrip = RPS_APRM_FLOW_TRIP_CLAMP
            
        else:
            if APRMFlux > RPS_APRM_SETDOWN_TRIP:
                RpsTripSignal = True
            for IRM in IRMs:
                if IRM["power"] > RPS_IRM_TRIP:
                    RpsTripSignal = True

        if RPVPress > RPS_HI_RPV_PRESSURE:
            RpsTripSignal = True
        
        if DWPress > RPS_HI_DW_TRIP:
            RpsTripSignal = True
            #all Loca Signals
        
        if APRMFlux > RPS_TSV_TRIP_POS:
            if TSVPos < RPS_TSV_TRIP_POS:
                RpsTripSignal = True

            if EHCPress < RPS_TCV_PRESS_TRIP:
                RpsTripSignal = True
        
        if ModeSw == model.ReactorMode.SHUTDOWN:
            if self.ModeSwTimer < 10:
                RpsTripSignal = True
                self.ModeSwTimer += delta
        else:
            self.ModeSwTimer = 0
        
        #TODO: APRM/IRM/OPRM Inop Trip
        #TODO: OPRM Trip
        #TODO: SDV Trip

        if RpsTripSignal == True and self.RPS_Trip_In == False:
            #init RPS Trip for channel
            self.RPS_Trip_In = True
            RPS_Logic.RPS_Trip_Ch[self.Train] = True
            self.Scram_Check()

    def Scram_Check(self):
        if RPS_Logic.RPS_Trip_Ch["A1"] == True or RPS_Logic.RPS_Trip_Ch["A2"]:
            if RPS_Logic.RPS_Trip_Ch["B1"] == True or RPS_Logic.RPS_Trip_Ch["B2"] == True:
                RPS_Logic.RPS_SYS_INIT = True
                #do other stuff when a scram occurs
            else:
                RPS_Logic.RPS_SYS_INIT = False

    def Reset_Logic(self):
        #find SDV bypass switch position
        #turn this channel RPS_Logic.RPS_Trip_Ch[self.Train] = False
        #Run Scram_Check

        #Todo - bypass switches and mode switch - shutdown scram
        RPS_Logic.RPS_Trip_Ch[self.Train] = False
        self.Scram_Check()
        pass


class EventHandler:
    def __init__(self):
        self.__connections = []

    def connect(self,func):
        self.__connections.append(func)

    def disconnect(self,func):
        self.__connections.remove(func)

    def fire(self, *args, **keywargs):
        for connection in self.__connections:
            connection(*args, **keywargs)

#global classes

ADS_1 = ADS_Logic("1")
ADS_2 = ADS_Logic("2")
RPS_A1 = RPS_Logic("A1")
RPS_A2 = RPS_Logic("A2")
RPS_B1 = RPS_Logic("B1")
RPS_B2 = RPS_Logic("B2")

def run(delta):
    
    #check alarms then run logic
    if reactor_inventory.rx_level_nr < RPV_LEVEL_3_in :
        model.alarms["ads_low_lvl_confirmed"]["alarm"] = True
    else:
        model.alarms["ads_low_lvl_confirmed"]["alarm"] = False
    model.alarms["ads_rhr_a_lpcs_permissive"]["alarm"] = bool(model.values["rhr_a_press"] > ADS_RHR_PRESS_PERMISSIVE_PSIG\
          or model.values["lpcs_press"] > ADS_LPCS_PRESS_PERMISSIVE_PSIG) 
    model.alarms["ads_rhr_bc_permissive"]["alarm"] = bool(model.values["rhr_b_press"] > ADS_RHR_PRESS_PERMISSIVE_PSIG\
          or model.values["rhr_c_press"] > ADS_RHR_PRESS_PERMISSIVE_PSIG)
    model.alarms["ads_div2_oos"]["alarm"] = bool(ADS_2.ADS_INHIBIT)
    model.alarms["ads_div1_oos"]["alarm"] = bool(ADS_1.ADS_INHIBIT)
    model.alarms["ads_sys_initiated_1"]["alarm"] = bool(ADS_1.ADS_SYS_INITIATED)
    model.alarms["ads_sys_initiated_2"]["alarm"] = bool(ADS_2.ADS_SYS_INITIATED)
    model.alarms["ads_timer_initiated_1"]["alarm"] = bool(ADS_1.ADS_Timer_Status)
    model.alarms["ads_timer_initiated_2"]["alarm"] = bool(ADS_2.ADS_Timer_Status)

    ADS_1.ADS_Run(reactor_inventory.rx_level_nr, reactor_inventory.rx_level_wr, model.values["rhr_a_press"]\
                , model.values["rhr_b_press"], model.values["rhr_c_press"], model.values["lpcs_press"],delta)
    ADS_2.ADS_Run(reactor_inventory.rx_level_nr, reactor_inventory.rx_level_wr, model.values["rhr_a_press"]\
                , model.values["rhr_b_press"], model.values["rhr_c_press"], model.values["lpcs_press"],delta)
    
    #TODO: Add RPS run to here
    
