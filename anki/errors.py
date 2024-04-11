# Warnings
class MalformedPacketWarning(Warning):
    """
    Received package did not conform to the Protocol.
    See https://anki.github.io/drive-sdk/docs/programming-guide
    """


class DuplicateScanWarning(Warning):
    """
    The map has already been scanned, but scan has been called anyway.
    This is not dangerous, but unneccessary
    """


class TrackPieceDecodeWarning(Warning):
    """The TrackPiece received from the vehicle was invalid"""


# Exceptions
class AnkiError(Exception):
    """Base class for all errors raised by this library"""


class VehicleNotFoundError(AnkiError):
    """Could not find a Supercar"""


class ConnectionFailedError(AnkiError):
    """Could not connect to the vehicle"""


class ConnectionDatabusError(ConnectionFailedError):
    """A data-bus error occured whilst connecting to the vehicle"""


class ConnectionTimedoutError(ConnectionFailedError):
    """The attempt to connect with the vehicle timed out"""


class DisconnectFailedError(AnkiError):
    """The attempt to disconnect from the vehicle failed"""


class DisconnectTimedoutError(DisconnectFailedError):
    """The disconnect attempt timed out"""


