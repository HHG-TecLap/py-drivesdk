from enum import Enum
from typing import Self

SERVICE_UUID = 'be15beef-6186-407e-8381-0bd89c4d8df4'
READ_CHAR_UUID = 'be15bee0-6186-407e-8381-0bd89c4d8df4'
WRITE_CHAR_UUID = 'be15bee1-6186-407e-8381-0bd89c4d8df4'

MAX_PACKET_PAYLOAD_SIZE = 18


class VehicleBattery:
    FULL_BATTERY = 4
    LOW_BATTERY = 5
    ON_CHARGER = 6
    _UNAVAILABLE = 7
    pass


"""
Not much information on the message types.
SET_LIGHTS payload boolean/byte-range? (Solved: Mask)
LIGHT_PATTERN incremental?
SET_SPEED range? Multiple bytes? (Solved: uint16_t)
CHANGE_LANE road offset in mm?
"""

"""
LIGHT_PATTERN: Some mask
SET_SPEED: uint16_t speed; uint16_t acceleration
SET_SDK: uint8_t enable_disable, uint8_t flags
"""


class ControllerMsg:
    DISCONNECT = 0x0d
    PING = 0x16
    VERSION_REQ = 0x18
    
    SET_LIGHTS = 0x1d
    LIGHT_PATTERN = 0x33
    
    SET_SPEED = 0x24
    CHANGE_LANE = 0x25
    CANCEL_LANE_CHANGE = 0x26
    TURN_180 = 0x32

    SET_SDK = 0x90
    pass


class VehicleMsg:
    PONG = 0x17
    VERSION_RESP = 0x19
    # Notify characteristic
    TRACK_PIECE_UPDATE = 0x27
    TRACK_PIECE_CHANGE = 0x29
    CHARGER_INFO = 0x3f
    DELOCALIZED = 0x2b
    pass


class TrackPieceType(Enum):
    """
    An enumerator for all supported track piece types.

    Thank you to https://github.com/BerndMuller/JAnki/
    """
    START = [33]
    FINISH = [34]
    STRAIGHT = [36, 39, 40, 48, 51]
    CURVE = [17, 18, 20, 23, 24, 27]
    INTERSECTION = [10]
    LAUNCH_START = [43]

    def __str__(self) -> str:
        return self.name
        pass

    @classmethod
    def try_enum(cls, value: int) -> Self:
        for enum in cls:
            if value in enum.value:
                return enum
                pass
            pass

        raise ValueError("piece value is not valid")
        pass
    pass
