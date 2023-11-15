from ..misc.track_pieces import TrackPiece
from .vehicle import Vehicle
from ..misc.const import TrackPieceType
import asyncio
import abc
from typing import TypeVar


def reorder_map(map: list[TrackPiece]):
    # Basically: Move the last piece to the front until START
    # is at index 0 and FINISH is at index -1 (i.e. the end)
    while not (map[0].type is TrackPieceType.START and map[-1].type is TrackPieceType.FINISH):
        map.insert(0, map.pop(-1))
        pass
    pass


class BaseScanner(abc.ABC):
    """Abstract base class for all custom scanners.
    Any subclasses of this must override the methods
    :meth:`BaseScanner.scan` :meth:`BaseScanner.align`.

    :param vehicle: :class:`Vehicle`
        The vehicle used for the scanning operation.
    """

    __slots__ = ("vehicle", "map")

    def __init__(self, vehicle: Vehicle):
        self.vehicle = vehicle
        self.map: list[TrackPiece] = []
        pass

    @abc.abstractmethod
    async def scan(self) -> list[TrackPiece]:
        """
        This method should scan in the map using various functionalities.
        The returned list of track pieces should begin with a type of
        `TrackPieceType.START` and end with `TrackPieceType.FINISH`.

        Returns
        -------
        :class:`list[TrackPiece]`
            The scanned map
        
        Raises
        ------
        """

    @abc.abstractmethod
    async def align(
        self,
        vehicle: Vehicle,
        *,
        target_previous_track_piece_type: TrackPieceType=TrackPieceType.FINISH
    ) -> None:
        """
        This method should be used to align a vehicle to the START piece.
        It is required for this method to work without a functional scan.

        :param vehicle: :class:`Vehicle`
            The vehicle to be aligned.
        
        Returns
        -------

        Raises
        ------
        """


class Scanner(BaseScanner):
    """A scanner object performs a simple map scan without any alignment.
    
    :param vehicle: :class:`Vehicle`
        The vehicle to perform the scan with
    """

    async def scan(self) -> list[TrackPiece]:
        """Perform the scan"""
        completed = [False]  # In a list because of global local issues
        track_types = []
        # This keeps track of the types we've visited
        # (could also be a set,
        # but TrackPieceType didn't have hashes back then)
        
        def watcher():
            track = self.vehicle._current_track_piece
            if track is not None:
                # track might be None for the first time this event is called
                self.map.append(track)
                track_types.append(track.type)
                if TrackPieceType.START in track_types and TrackPieceType.FINISH in track_types:
                    # This marks the scan as complete
                    # once both START and FINISH have been found
                    completed[0] = True

        self.vehicle.on_track_piece_change = watcher
        
        await self.vehicle.set_speed(300)
        while not completed[0]:
            # Drive along until the scan is marked as complete.
            # (This does NOT cause parallelity issues because we're
            # running the watcher synchronously in the background)
            await asyncio.sleep(0.5)
            pass

        self.vehicle.on_track_piece_change = lambda: None
        await self.vehicle.stop()

        reorder_map(self.map)
        # Assure that START is at the beginning and FINISH is at the end

        return self.map
        pass

    async def align(
        self,
        vehicle: Vehicle,
        *,
        target_previous_track_piece_type: TrackPieceType=TrackPieceType.FINISH
    ) -> None:
        """
        Aligns a vehicle to the START piece

        :param vehicle: :class:`Vehicle`
            The vehicle to align
        """
        await vehicle.align(
            target_previous_track_piece_type=target_previous_track_piece_type
        )
        pass
    pass


_Scanner = TypeVar("_Scanner", bound=BaseScanner)
_ScannerType = type[_Scanner]
