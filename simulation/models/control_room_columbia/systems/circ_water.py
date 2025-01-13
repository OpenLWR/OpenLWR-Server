from simulation.constants import pump
from simulation.models.control_room_columbia.general_physics import air_system as air #TODO: use a generalized version for valves instead

CW_P_1A = None
CW_V_1A = None #P1A discharge butterfly

def init():

    global CW_P_1A
    global CW_V_1A

    CW_P_1A = pump.MotorPump("cw_p_1a",bus="1",horsepower=5060,rated_rpm=1800,rated_discharge_press=40,rated_flow=186000)
    CW_V_1A = air.Valve(0,"cw_v_1a",True,False,60,air.SupplyElectric())

    print("Circ water init")

def run(delta):
    
    CW_P_1A.calculate(delta)
    CW_V_1A.calculate()

    #B and C CW pump trip at level two (https://adamswebsearch2.nrc.gov/webSearch2/main.jsp?AccessionNumber=ML070740688)

    #switch START position opens the discharge valve
    #switch STOP position strokes closed the discharge valve, stops pump at 15% open and continues closing after
    #switch PTL position strokes closed the discharge valve asap

    