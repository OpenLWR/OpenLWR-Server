from simulation.models.control_room_columbia.general_physics import ac_power
from simulation.models.control_room_columbia import model

def get_phase(name):
    if name in ac_power.sources:
        return ac_power.sources[name].info["phase"]
    
    return ac_power.busses[name].info["phase"]

class SyncSelector():

    def __init__(self,sync_name):
        self.selectors = {}
        self.synchroscope = sync_name

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



synchroscopes = []

def initialize():
    sync = SyncSelector("main_generator_sync")
    sync.add_selector("sync_cb_4885","gen_bus","GRID","cb_4885")
    sync.add_selector("sync_cb_4888","gen_bus","GRID","cb_4888")
    synchroscopes.append(sync)

    sync = SyncSelector("div_1_sync")
    sync.add_selector("sync_cb_dg1_7","DG1","7","cb_dg1_7")
    synchroscopes.append(sync)

def run():
    for synchroscope in synchroscopes:
        synchroscope.check_selectors()