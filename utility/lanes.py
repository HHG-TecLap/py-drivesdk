import dataclasses

def __add_constants__(cls : "_Lane"):
    for position, name in cls.__LANE_EQUIVS__.items():
        setattr(cls,name,cls(name,position))
        pass

    return cls
    pass

@dataclasses.dataclass(frozen=True,unsafe_hash=False,slots=True)
class _Lane:
    __LANE_EQUIVS__ = {}

    lane_name : str
    lane_position : float


    @classmethod
    def get_closest_lane(cls, position : float):
        _, lane_val = min({abs(k-position) : k for k, v in cls.__LANE_EQUIVS__.items()}.items(),key=lambda v: v[0])
        
        return cls(cls.__LANE_EQUIVS__[lane_val],lane_val)
        pass
    @classmethod
    def by_name(cls, name : str):
        if not name in cls.__LANE_EQUIVS__.values(): raise ValueError("Lane does not exist for the chosen type")
        rev_equivs = {v:k for k,v in cls.__LANE_EQUIVS__.items()}

        return cls(name,rev_equivs[name])
        pass

    @classmethod
    def get_all(cls):
        return [cls(name,position) for position, name in cls.__LANE_EQUIVS__.items()]
        pass

    def __eq__(self, other : "_Lane"): return self.lane_position == other.lane_position
    def __ne__(self, other : "_Lane"): return self.lane_position != other.lane_position
    def __gt__(self, other : "_Lane"): return self.lane_position > other.lane_position
    def __lt__(self, other : "_Lane"): return self.lane_position < other.lane_position
    def __ge__(self, other : "_Lane"): return self.lane_position >= other.lane_position
    def __le__(self, other : "_Lane"): return self.lane_position <= other.lane_position


    def __str__(self):
        return self.lane_name
        pass
    pass

@__add_constants__
class Lane3(_Lane):
    __LANE_EQUIVS__ = {
        -60: "LEFT",
        0  : "MIDDLE",
        60 : "RIGHT"
    }
    pass

@__add_constants__
class Lane4(_Lane):
    __LANE_EQUIVS__ = {
        -60: "LEFT_2",
        -30: "LEFT_1",
        +30: "RIGHT_1",
        +60: "RIGHT_2"
    }
    pass