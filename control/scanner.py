"""TODO: Fix vehicle finishing too early when starting from different piece than start"""

from ..utility.track_pieces import TrackPiece
from ..vehicle import Vehicle
from ..utility.const import TrackPieceTypes
import asyncio

def reorder_map(map : list[TrackPiece]):
    while not (map[0].type is TrackPieceTypes.START and map[-1].type is TrackPieceTypes.FINISH):
        map.insert(0,map.pop(-1))
        pass
    pass

class Scanner:
    __slots__ = ["vehicle","map"]
    def __init__(self, vehicle : Vehicle):
        self.vehicle = vehicle
        self.map : list[TrackPiece] = []
        pass

    async def scan(self) -> list[TrackPiece]:
        completed = [False] # In a list because of global local issues
        track_types = []
        def watcher():
            track = self.vehicle._current_track_piece
            if track is not None:
                self.map.append(track)
                track_types.append(track.type)
                if TrackPieceTypes.START in track_types and TrackPieceTypes.FINISH in track_types:
                    completed[0] = True
                    pass
                pass
            pass

        self.vehicle.on_track_piece_change = watcher
        
        await self.vehicle.setSpeed(300)
        while not completed[0]:
            await asyncio.sleep(0.5)
            pass

        self.vehicle.on_track_piece_change = lambda: None
        await self.vehicle.stop()

        reorder_map(self.map)

        return self.map
        pass
    pass