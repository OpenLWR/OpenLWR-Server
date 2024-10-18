from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory

#Engineered Safeguard Feature Actuation System

RPV_LEVEL_1_in = -129
RPV_LEVEL_2_in = -51
RPV_LEVEL_3_in = 13
RPV_LEVEL_8_in = 54

PSIG_TO_PASCAL = 6895

# follow up on this value
# using the midpoint from ITS LCO 3.3.5.1 table 4.d/4.c looks about right
ADS_RHR_PRESS_PERMISSIVE_PSIG = 125
ADS_RHR_PRESS_PERMISSIVE_PA = ADS_RHR_PRESS_PERMISSIVE_PSIG * PSIG_TO_PASCAL
ADS_LPCS_PRESS_PERMISSIVE_PSIG = 145
ADS_LPCS_PRESS_PERMISSIVE_PA = ADS_LPCS_PRESS_PERMISSIVE_PSIG * PSIG_TO_PASCAL
ADS_DELAY_TIMER_sec = 105


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


        if self.Train == 1:
            if RHR_A_PRESS > ADS_RHR_PRESS_PERMISSIVE_PA or LPCS_PRESS > ADS_LPCS_PRESS_PERMISSIVE_PA:
                if self.ADS_INHIBIT == False:
                    self.ADS_INITIATE_1()
                    self.ADS_INITIATE_2()
        
        if self.Train == 2:
            if RHR_B_PRESS > ADS_RHR_PRESS_PERMISSIVE_PA or RHR_C_PRESS > ADS_RHR_PRESS_PERMISSIVE_PA:
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

ADS_1 = ADS_Logic("1")
ADS_2 = ADS_Logic("2")

def run(delta):
    
    #check alarms then run logic
    if reactor_inventory.rx_level_nr < RPV_LEVEL_3_in :
        model.alarms["ads_low_lvl_confirmed"]["alarm"] = True
    else:
        model.alarms["ads_low_lvl_confirmed"]["alarm"]  = False
    model.alarms["ads_rhr_a_lpcs_permissive"]["alarm"] = bool(model.values["rhr_a_press"] > ADS_RHR_PRESS_PERMISSIVE_PA\
          or model.values["lpcs_press"] > ADS_LPCS_PRESS_PERMISSIVE_PA) 
    model.alarms["ads_rhr_bc_permissive"]["alarm"] = bool(model.values["rhr_b_press"] > ADS_RHR_PRESS_PERMISSIVE_PA\
          or model.values["rhr_c_press"] > ADS_RHR_PRESS_PERMISSIVE_PA)
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
    
