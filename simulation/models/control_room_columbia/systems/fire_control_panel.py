from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.systems import fire

def run(delta):
    model.alarms["tg_bldg_471_elect_swgr_bay"]["alarm"] = fire.SLCs["TG BLDG 471 ELECT SWGR"].fire or fire.SLCs["TG BLDG 471 ELECT SWGR"].trouble
    model.alarms["tg_bldg_471_elect_swgr_bay_trouble"]["alarm"] = fire.SLCs["TG BLDG 471 ELECT SWGR"].trouble
    model.alarms["tg_bldg_471_elect_swgr_bay_fire"]["alarm"] = fire.SLCs["TG BLDG 471 ELECT SWGR"].fire

    model.alarms["sys_7_wet_pipe_tg_bldg_471_elect_swgr_bay"]["alarm"] = fire.SLCs["SYS 7 WET PIPE TG BLDG 471 ELECT SWGR"].fire or fire.SLCs["SYS 7 WET PIPE TG BLDG 471 ELECT SWGR"].trouble
    model.alarms["sys_7_wet_pipe_tg_bldg_471_elect_swgr_bay_trouble"]["alarm"] = fire.SLCs["SYS 7 WET PIPE TG BLDG 471 ELECT SWGR"].trouble
    model.alarms["sys_7_wet_pipe_tg_bldg_471_elect_swgr_bay_fire"]["alarm"] = fire.SLCs["SYS 7 WET PIPE TG BLDG 471 ELECT SWGR"].fire