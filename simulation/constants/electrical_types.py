from enum import IntEnum

class ElectricalType(IntEnum):
    BREAKER = 0,
    TRANSFORMER = 1,
    BUS = 2,
    SOURCE = 3,