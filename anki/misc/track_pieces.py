from .const import TrackPieceType
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class TrackPiece():
    """
    This class represents the different pieces of the track. 
    It includes the type of the track piece and whether or not it turns clockwise.
    
    You should not be creating these manually.
    
    :param loc: :class:`int`
        The loc value send by the supercar. I'm not sure what it means either
    
    :param type: :class:`TrackPieceType`
        The type of track piece
    
    :param clockwise: :class:`bool`
        Whether or not this track piece turns in a clockwise direction
    """
    loc : int
    type : TrackPieceType
    clockwise : bool = field(compare=False)

    @staticmethod
    def from_raw(
        loc: int, 
        piece_val: int, 
        clockwise: int
    ) -> "TrackPiece":
        return TrackPiece(
            loc,
            TrackPieceType.try_enum(piece_val),
            clockwise > 30
        )
        pass
    pass