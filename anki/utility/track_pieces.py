from .const import TrackPieceType, TrackPieceTypes
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class TrackPiece():
    """This class represents the different pieces of the track. It includes the type of the track piece and whether or not it turns clockwise.\n
    You should not be creating these manually.
    ## Parameters
    + loc: The loc value send by the supercar. I'm not sure what it means either
    + piece_val: The piece value sent by the supercar. The actual value might vary even when the type does not
    + clockwise: An integer denoting whether or not this piece turns clockwise
    """
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