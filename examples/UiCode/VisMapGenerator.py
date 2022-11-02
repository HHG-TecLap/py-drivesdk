from warnings import warn
from anki import TrackPiece, TrackPieceTypes

__all__ = ("generate")


Vismap = list[list[list[TrackPiece]]]

_ORIENTATIONS=((1,0),(0,-1),(-1,0),(0,1))
def _next_orientation(orientation: tuple[int,int], is_clockwise: bool) -> tuple[int,int]:
    new_index = _ORIENTATIONS.index(orientation) + (1 if is_clockwise else -1)
    return _ORIENTATIONS[new_index%len(_ORIENTATIONS)]

def _expand_right(vismap: Vismap):
    vismap.append(
        [[] for _ in range(len(vismap[0]))]
        # len(vismap[0]) is the column length (i.e. row count)
    )
    pass

def _expand_left(vismap: Vismap):
    vismap.insert(
        0,
        [[] for _ in range(len(vismap[0]))]
        # len(vismap[0]) is the column length (i.e. row count)
    )
    pass

def _expand_up(vismap: Vismap):
    for column in vismap:
        column.insert(0,[])
        pass
    pass

def _expand_down(vismap: Vismap):
    for column in vismap:
        column.append([])
        pass
    pass

def generate(track_map: list[TrackPiece]) -> Vismap:
    """Creates a 3d map of the track from the 1d version passed as an argument"""
    vismap: Vismap = [[[]]]

    head = [0,0]
    orientation = (1,0)
    for piece in track_map:
        head[0] += orientation[0]
        head[1] += orientation[1]

        # Adjust vismap when needed
        if head[0] > len(vismap)-1: 
            # If not enough columns to the right
            _expand_right(vismap)
            pass
        elif head[0] < 0: 
            # If not enough columns to the left
            _expand_left(vismap)
            head[0]+=1
            pass
        if head[1] > len(vismap[0])-1:
            # If not enough rows down
            _expand_down(vismap)
            pass
        elif head[1] < 0:
            # If not enough rows up
            _expand_up(vismap)
            head[1]+=1
            # Incrementing head, because the vismap has now shifted
            pass
        
        # Set new orientation
        if piece.type == TrackPieceTypes.CURVE:
            orientation = _next_orientation(orientation, piece.clockwise)
            pass
        
        # Adding vismap entry if doing so will not cause two intersections to overlay
        # This is done so that the vismap doesn't always have two intersections for every intersection that exists
        working_cell = vismap[head[0]][head[1]]
        if not(piece.type == TrackPieceTypes.INTERSECTION 
        and len(working_cell) > 0
        and all([
            check.type == TrackPieceTypes.INTERSECTION 
            for check in working_cell
        ])):
            warn(
                "Ignoring an intersection piece. If you have stacked two intersection pieces, this will cause bugs. If not, you can ignore this warning.",
                stacklevel=2)
            working_cell.append(piece)
            pass
        pass

    return vismap
    pass
