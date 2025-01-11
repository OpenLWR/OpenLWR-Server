from simulation.constants import pump

CW_P_1A = None

def init():

    CW_P_1A = pump.MotorPump("cw_p_1a",bus="1",horsepower=5060,rated_rpm=1800,rated_discharge_press=40,rated_flow=186000)

    print("Circ water init")

def run(delta):
    
    CW_P_1A.calculate(delta)