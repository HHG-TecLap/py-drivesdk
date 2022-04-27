# Warnings
class MalformedPacketWarning(Warning):
    """Received package did not conform to the Protocol. See https://anki.github.io/drive-sdk/docs/programming-guide"""
    pass

class DuplicateScanWarning(Warning):
    """The map has already been scanned, but scan has been called anyway. This is not dangerous, but unneccessary"""
    pass

# Exceptions
class AnkiException(Exception): 
    """Base class for all errors raised by this library"""
    pass

class VehicleNotFound(AnkiException):
    """Could not find a Supercar"""
    pass

class ConnectionFailedException(AnkiException):
    """Could not connect to the vehicle"""
    pass

class ConnectionDatabusException(ConnectionFailedException):
    """A data-bus error occured whilst connecting to the vehicle"""
    pass

class ConnectionTimedOutException(ConnectionFailedException):
    """The attempt to connect with the vehicle timed out"""
    pass

class DisconnectFailedException(AnkiException):
    """The attempt to disconnect from the vehicle failed"""
    pass