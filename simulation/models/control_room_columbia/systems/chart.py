
from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory

class RecorderDX1000:
    def __init__(self,name):
        self.name = name
        self.channels = {}
        self.channel_alarms = {}
        self.allow_reprogram = False
        self.sampling_enabled = False #Disables drawing of graphs

        self.page = 1

        self.buttons = {
            "ENTER" : False,
            "LEFTARROW" : False,
            "RIGHTARROW" : False,
            "UPARROW" : False,
            "DOWNARROW" : False,
            "MENU" : False,
            "ESCAPE" : False,
        }

        model.recorders[self.name] = self

    def set_allow_reprogram(self,allow):
        self.allow_reprogram = allow

    def add_channel(self,channel_name,unit,initial_value=0,low_over=0,over=0):
        self.channels[channel_name] = {"text":str(initial_value),"unit":unit,"value":initial_value,"+over":over,"-over":low_over}

    def bind_alarm(self,channel_name,alarm_type,limit,hysteresis):
        self.channel_alarms[channel_name] = {"alarm_type":alarm_type,"limit":limit,"hysteresis":hysteresis}

    def set_channel_value(self,channel_name,value):
        self.channels[channel_name]["value"] = value

    def button_updated(self,button,state):
        if button in self.buttons:
            self.buttons[button] = state

    def calculate(self):
        for channel in self.channels:
            channel = self.channels[channel]
            if channel["value"] > channel["+over"]:
                channel["text"] = "+Over"
            elif channel["value"] < channel["-over"]:
                channel["text"] = "-Over"
            else:
                channel["text"] = str(round(channel["value"],3))

        #buttons

        if self.buttons["MENU"]:

            #any value display page to settings page
            if self.page == 1 or self.page == 2:
                self.page = 3

        if self.buttons["ESCAPE"]:

            #menu page back to regular
            #TODO: save the view selected
            if self.page == 3:
                self.page = 1



    def change_page(self,page):
        self.page = page

    #TODO: Alarms

    #TODO: Trend


def initialize():
    a = RecorderDX1000("601RPV")
    a.add_channel("RPV LEVEL WR","INCHES",0,20,183) #TODO: what were the limits of RPV WR?


def run():
    model.recorders["601RPV"].channels["RPV LEVEL WR"]["value"] = reactor_inventory.rx_level_wr

    for recorder in model.recorders:
        model.recorders[recorder].calculate()
