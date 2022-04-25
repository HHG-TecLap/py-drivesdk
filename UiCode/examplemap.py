from anki import TrackPiece, TrackPieceTypes
from anki.utility.const import RawTrackPieces

def g(vals, clockwise = 0):
    return TrackPiece(0,vals[0],clockwise)
    pass

START = RawTrackPieces.START
CURVE = RawTrackPieces.CURVE
STRAIGHT = RawTrackPieces.STRAIGHT
INTERSECTION = RawTrackPieces.INTERSECTION
FINISH = RawTrackPieces.FINISH

map = (
    g(START),
    g(CURVE,255),
    g(INTERSECTION),
    g(INTERSECTION),
    g(CURVE,255),
    g(STRAIGHT),
    g(CURVE,255),
    g(INTERSECTION),
    g(CURVE,255),
    g(CURVE,255),
    g(INTERSECTION),
    g(STRAIGHT),
    g(CURVE,255),
    g(STRAIGHT),
    g(CURVE,255),
    g(FINISH)
)