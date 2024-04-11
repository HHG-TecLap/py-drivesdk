from warnings import warn
from enum import Enum
from typing import TypeVar, Self


class BaseLane(float, Enum):
    """
    The base class for all Lanes.
    This class does not provide any lanes of its own, but can be inherited from
    to create your own lane system.
    Pre-configured children of this class are :class:`Lane3` and :class:`Lane4`
    """

    @classmethod
    def get_closest_lane(cls, position: float) -> Self:
        """
        Returns the lane closest to the entered position.

        :param position: :class:`float`
            The position offset from the centre of the road in millimetres.

        Raises
        ------
        :class:`RuntimeError`
            The this method is being called with does not have any specified lanes.
        """
        try:
            return min(cls, key=lambda v: abs(position - v.value))
        except ValueError as e:
            raise RuntimeError(f"Subclass {cls.__name__} of BaseLane has no lanes") from e
            pass
        pass

    @classmethod
    def by_name(cls, name: str):
        """
        Get a lane by the lane's name.

        :param name: :class:`str`
            The name of the lane

        Raises
        ------
        :class:`ValueError`
            The name passed does not refer to an existing lane
        """
        try:
            return next(filter(lambda v: v.name == name, cls))
        except StopIteration as e:
            raise ValueError("Lane does not exist for the chosen type") from e
            pass
        pass

    def __str__(self) -> str:
        return self.name
    pass


class Lane3(BaseLane):
    """
    A lane class that supports 3 different lanes.
    Values indicate the millimetre distance from the road centre.
    """

    LEFT = -60
    MIDDLE = 0
    RIGHT = 60
    pass


class Lane4(BaseLane):
    """
    A lane class that supports 4 different lanes.
    Values indicate the millimetre distance from the road centre.
    """
    LEFT_2 = -60
    LEFT_1 = -30
    RIGHT_1 = 30
    RIGHT_2 = 60
    pass


_Lane = TypeVar('_Lane', bound=BaseLane)
_LaneType = type[_Lane]
