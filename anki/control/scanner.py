from ..utility.track_pieces import TrackPiece
from .vehicle import Vehicle
from ..utility.const import TrackPieceTypes
import asyncio

def reorderMap(map : list[TrackPiece]):
    # Basically: Move the last piece to the front until START is at index 0 and FINISH is at index -1 (i.e. the end)
    while not (map[0].type is TrackPieceTypes.START and map[-1].type is TrackPieceTypes.FINISH):
        map.insert(0,map.pop(-1))
        pass
    pass

class Scanner:
    """A scanner object performs a simple map scan without any alignment.
    
    ## Params\n
    + vehicle: The `Vehicle` object to perform the scan with"""

    __slots__ = ["vehicle","map"]
    def __init__(self, vehicle : Vehicle):
        self.vehicle = vehicle
        self.map : list[TrackPiece] = []
        pass

    async def scan(self) -> list[TrackPiece]:
        """Perform the scan"""
        completed = [False] # In a list because of global local issues
        track_types = [] # This keeps track of the types we've visited (could also be a set, but TrackPieceType didn't have hashes back then)
        def watcher():
            track = self.vehicle._current_track_piece
            if track is not None: # track might be None for the first time this event is called
                self.map.append(track)
                track_types.append(track.type)
                if TrackPieceTypes.START in track_types and TrackPieceTypes.FINISH in track_types: # This marks the scan as complete once both START and FINISH have been found
                    completed[0] = True
                    pass
                pass
            pass

        self.vehicle.on_track_piece_change = watcher
        
        await self.vehicle.setSpeed(300)
        while not completed[0]: # Drive along until the scan is marked as complete. (This does NOT cause parallelity issues because we're running the watcher synchronously in the background)
            await asyncio.sleep(0.5)
            pass

        self.vehicle.on_track_piece_change = lambda: None
        await self.vehicle.stop()

        reorderMap(self.map) # Assure that START is at the beginning and FINISH is at the end

        return self.map
        pass
    pass