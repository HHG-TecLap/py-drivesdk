from .const import TrackPieceType, TrackPieceTypes
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class TrackPiece():
    loc : int
    type : TrackPieceType
    clockwise : bool = field(compare=False)

    @staticmethod
    def from_raw(loc : int, piece_val : int, clockwise : int) -> "TrackPiece":
        return TrackPiece(
            loc,
            TrackPieceTypes.try_type(piece_val),
            clockwise > 30
        )
        pass
    pass