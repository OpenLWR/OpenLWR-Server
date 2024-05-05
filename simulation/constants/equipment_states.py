from enum import IntEnum

class EquipmentStates(IntEnum):
    RUNNING = 0, #Running/Enabled/Spinning/Energized
    STARTING = 1,
    STOPPING = 2,
    STOPPED = 3,