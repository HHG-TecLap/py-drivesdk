from dataclasses import dataclass
from enum import Enum
from warnings import warn

SERVICE_UUID    = 'be15beef-6186-407e-8381-0bd89c4d8df4'
READ_CHAR_UUID   = 'be15bee0-6186-407e-8381-0bd89c4d8df4'
WRITE_CHAR_UUID = 'be15bee1-6186-407e-8381-0bd89c4d8df4'

MAX_PACKET_PAYLOAD_SIZE = 18

class VehicleBattery:
    FULL_BATTERY = 4
    LOW_BATTERY  = 5
    ON_CHARGER   = 6
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
    DISCONNECT = b"\x0d"
    PING = b"\x16"
    VERSION_REQ = b"\x18"
    
    SET_LIGHTS = b"\x1d"
    LIGHT_PATTERN = b"\x33"
    
    SET_SPEED  = b"\x24"
    CHANGE_LANE = b"\x25"
    CANCEL_LANE_CHANGE = b"\x26"
    TURN_180 = b"\x32"

    SET_SDK = b"\x90"
    pass

class VehicleMsg:
    PONG = b"\x17"
    VERSION_RESP = b"\x19"
    # Notify characteristic
    TRACK_PIECE_UPDATE = 39
    TRACK_PIECE_CHANGE = 41
    CHARGER_INFO = 63
    DELOCALIZED = 0x2b
    pass

# class RawTrackPieces:
#     """Thank you to https://github.com/BerndMuller/JAnki/"""
#     START = [33]
#     FINISH = [34]
#     STRAIGHT = [36,39,40,48,51]
#     CURVE = [17,18,20,23,24,27]
#     INTERSECTION = [10]
#     pass

# @dataclass(frozen=True,slots=True)
# class TrackPieceType:
#     name : str
#     pass

# class TrackPieceTypes:

#     START        = TrackPieceType("START")
#     FINISH       = TrackPieceType("FINISH")
#     STRAIGHT     = TrackPieceType("STRAIGHT")
#     CURVE        = TrackPieceType("CURVE")
#     INTERSECTION = TrackPieceType("INTERSECTION")

#     @classmethod
#     def try_type(cls,piece_value : int) -> object:
#         if piece_value in RawTrackPieces.START:          return cls.START
#         elif piece_value in RawTrackPieces.FINISH:       return cls.FINISH
#         elif piece_value in RawTrackPieces.STRAIGHT:     return cls.STRAIGHT
#         elif piece_value in RawTrackPieces.CURVE:        return cls.CURVE
#         elif piece_value in RawTrackPieces.INTERSECTION: return cls.INTERSECTION
#         else: raise ValueError("Piece value is not valid")
#         pass
    
#     @classmethod
#     def as_str(cls, piece : TrackPieceType) -> str:
#         warn("TrackPieceTypes.as_str is deprecated. Use TrackPiece.name instead",DeprecationWarning)

#         return piece.name
#         pass
#     pass

class TrackPieceType(Enum):
    """
    An enumerator for all supported track piece types.

    Thank you to https://github.com/BerndMuller/JAnki/
    """
    START = [33]
    FINISH = [34]
    STRAIGHT = [36,39,40,48,51]
    CURVE = [17,18,20,23,24,27]
    INTERSECTION = [10]
    LAUNCH_START = [43]

    def __str__(self) -> str:
        return self.name
        pass

    @staticmethod
    def try_enum(value: int):
        for enum in TrackPieceType:
            if value in enum.value:
                return enum
                pass
            pass

        raise ValueError("piece value is not valid")
        pass
    pass