from simulation.models.control_room_columbia.general_physics import ac_power
from simulation.models.control_room_columbia import model

def get_phase(name):
    if name in ac_power.sources:
        return ac_power.sources[name].info["phase"]
    
    return ac_power.busses[name].info["phase"]

def get_voltage(name):
    if name in ac_power.sources:
        return ac_power.sources[name].info["voltage"]
    
    return ac_power.busses[name].info["voltage"]

class SyncSelector():

    def __init__(self,sync_name):
        self.selectors = {}
        self.synchroscope = sync_name
        self.incoming = None
        self.running = None

    def add_voltage_gauges(self,incoming,running):
        self.incoming=incoming
        self.running=running

    def add_selector(self,name,incoming,running,breaker):
        
        self.selectors[name] = {"incoming" : incoming, "running" : running, "breaker" : breaker}

        ac_power.breakers[breaker].info["sync_sel"] = True

    def check_selectors(self):

        active_selector = ""

        for selector in self.selectors:
    
            if model.switches[selector]["position"] != 1:
                active_selector = selector
                break

        if active_selector != "":
            sel = self.selectors[active_selector]
            model.values[self.synchroscope] = get_phase(sel["running"])-get_phase(sel["incoming"])

            if model.switches[active_selector]["position"] == 0:
                ac_power.breakers[sel["breaker"]].info["sync"] = True

            if self.incoming != None and self.running != None:
                model.values[self.incoming] = get_voltage(sel["incoming"])
                model.values[self.running] = get_voltage(sel["running"])
        else:

            if self.incoming != None and self.running != None:
                model.values[self.incoming] = 0
                model.values[self.running] = 0


synchroscopes = []

def initialize():
    sync = SyncSelector("main_generator_sync")
    sync.add_selector("sync_cb_4885","main_bus","ASHE500","cb_4885")
    sync.add_selector("sync_cb_4888","main_bus","ASHE500","cb_4888")
    synchroscopes.append(sync)

    sync = SyncSelector("div_1_sync")
    sync.add_voltage_gauges("sm7incoming","sm7running")
    sync.add_selector("sync_cb_dg1_7","DG1","7","cb_dg1_7")
    sync.add_selector("sync_cb_b7","b_bus","7","cb_b7")
    sync.add_selector("sync_cb_7_1","1","7","cb_1_7")
    synchroscopes.append(sync)

    sync = SyncSelector("div_2_sync")
    sync.add_selector("sync_cb_dg2_8","DG2","8","cb_dg2_8")
    sync.add_selector("sync_cb_b8","b_bus","8","cb_b8")
    sync.add_selector("sync_cb_8_3","3","8","cb_3_8")
    synchroscopes.append(sync)

def run():
    for synchroscope in synchroscopes:
        synchroscope.check_selectors()