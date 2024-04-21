from enum import IntEnum

class ClientPackets(IntEnum):
    SWITCH_PARAMETERS_UPDATE = 2

class ServerPackets(IntEnum):
    METER_PARAMETERS_UPDATE = 0
    USER_LOGOUT = 1