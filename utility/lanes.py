import dataclasses

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


    def __str__(self):
        return self.lane_name
        pass
    pass

class Lane3(_Lane):
    """TODO: Change these values to more accurate ones"""
    __LANE_EQUIVS__ = {
        -50: "LEFT",
        0  : "MIDDLE",
        50 : "RIGHT"
    }
    pass

class Lane4(_Lane):
    """TODO: Change these values as well"""
    __LANE_EQUIVS__ = {
        -50: "LEFT_2",
        -25: "LEFT_1",
        +25: "RIGHT_1",
        +50: "RIGHT_2"
    }
    pass