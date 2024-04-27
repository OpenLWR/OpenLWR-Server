from enum import IntEnum

class AnnunciatorStates(IntEnum):
    CLEAR = 0
    ACTIVE = 1
    ACKNOWLEDGED = 2
    ACTIVE_CLEAR = 3