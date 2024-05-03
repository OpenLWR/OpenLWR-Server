from enum import IntEnum

class ClientPackets(IntEnum):
    SWITCH_PARAMETERS_UPDATE = 2
    BUTTON_PARAMETERS_UPDATE = 6
    PLAYER_POSITION_PARAMETERS_UPDATE = 9
    ROD_SELECT_UPDATE = 11,
    USER_LOGIN = 12,
    SYNCHRONIZE = 14,

class ServerPackets(IntEnum):
    METER_PARAMETERS_UPDATE = 0
    USER_LOGOUT = 1
    SWITCH_PARAMETERS_UPDATE = 3
    INDICATOR_PARAMETERS_UPDATE = 4
    ALARM_PARAMETERS_UPDATE = 5
    BUTTON_PARAMETERS_UPDATE = 7
    PLAYER_POSITION_PARAMETERS_UPDATE = 8
    ROD_POSITION_PARAMETERS_UPDATE = 10
    USER_LOGIN_ACK = 13,