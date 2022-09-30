from .deprecated_alias import deprecated_alias, AliasMeta
import dataclasses


@dataclasses.dataclass(frozen=True,unsafe_hash=False,slots=True)
class BaseLane(metaclass=AliasMeta):
    """The raw base class for lane types. Inherit from this class to create your own lane type.
    
    Parameters
    ----------
    :param lane_name: :class:`str`
        The name of the lane
    :param lane_position: :class:`float`
        The optimal position for this lane
    """

    __LANE_EQUIVS__ = {}

    lane_name : str
    lane_position : float

    
    def __init_subclass__(cls) -> None:
        for position, name in cls.__LANE_EQUIVS__.items():
            setattr(cls,name,cls(name,position))
            pass
        pass

    @classmethod
    @deprecated_alias("getClosestLane")
    def get_closest_lane(cls, position : float):
        _, lane_val = min([
            (abs(k-position), k) 
            for k, v in cls.__LANE_EQUIVS__.items()
        ],key=lambda v: v[0]) 
        # Find the name->offset pairing with minimal distance to the position
        
        return cls(cls.__LANE_EQUIVS__[lane_val],lane_val) # Construct BaseLane object around raw info
        pass
    
    @classmethod
    @deprecated_alias("byName")
    def by_name(cls, name : str):
        if not name in cls.__LANE_EQUIVS__.values(): raise ValueError("Lane does not exist for the chosen type")
        rev_equivs = {v:k for k,v in cls.__LANE_EQUIVS__.items()}

        return cls(name,rev_equivs[name])
        pass

    @classmethod
    @deprecated_alias("getAll")
    def get_all(cls):
        return [cls(name,position) for position, name in cls.__LANE_EQUIVS__.items()]
        pass
    
    # Implemented all equalities for better speed
    def __eq__(self, other : "BaseLane"): return self.lane_position == other.lane_position
    def __ne__(self, other : "BaseLane"): return self.lane_position != other.lane_position
    def __gt__(self, other : "BaseLane"): return self.lane_position > other.lane_position
    def __lt__(self, other : "BaseLane"): return self.lane_position < other.lane_position
    def __ge__(self, other : "BaseLane"): return self.lane_position >= other.lane_position
    def __le__(self, other : "BaseLane"): return self.lane_position <= other.lane_position


    def __str__(self):
        # This improves readability over BaseLane(lane_name="MIDDLE",lane_position=0)
        return self.lane_name
        pass
    pass

class Lane3(BaseLane):
    """A lane type for programs using 3 lanes (left, middle, right)
    This holds three constants (ordered left-to-right):
    + `Lane3.LEFT`
    + `Lane3.MIDDLE`
    + `Lane3.RIGHT`
    """
    __LANE_EQUIVS__ = {
        -60: "LEFT",
        0  : "MIDDLE",
        60 : "RIGHT"
    }
    pass

class Lane4(BaseLane):
    """A lane type for programs using 4 lanes (leftmost, left-middle, right-middle, rightmost)
    This holds three constants (ordered left-to-right):
    + `Lane4.LEFT_2`
    + `Lane4.LEFT_1`
    + `Lane4.RIGHT_1`
    + `Lane4.RIGHT_2`
    """
    __LANE_EQUIVS__ = {
        -60: "LEFT_2",
        -30: "LEFT_1",
        +30: "RIGHT_1",
        +60: "RIGHT_2"
    }
    pass