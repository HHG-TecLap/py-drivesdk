from .const import TrackPieceTypes

class TrackPiece():
    __slots__ = ["type","loc","clockwise"]
    def __init__(self, loc : int, piece_val : int, clockwise : int) -> None:
        object.__setattr__(self,"type",TrackPieceTypes.try_type(piece_val))
        object.__setattr__(self,"loc",loc)
        object.__setattr__(self,"clockwise",clockwise > 30)
        pass

    def __setattr__(self, name: str, value) -> None:
        raise NotImplementedError("This instance is frozen and cannot be written to")
        pass

    def __repr__(self) -> str:
        return f"<TrackPiece type={TrackPieceTypes.as_str(self.type)}; loc={self.loc}; clockwise={self.clockwise}>"
        pass

    def __eq__(self,other : object) -> bool:
        if not isinstance(other,self.__class__): raise TypeError("Comparison between {0} and {1} is not possible".format(self.__class__,other.__class__))
        return self.type is other.type and self.loc is other.loc
        pass
    pass