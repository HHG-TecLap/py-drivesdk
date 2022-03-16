class MalformedPacketWarning(Warning):
    """Received package did not conform to the Protocol. See https://anki.github.io/drive-sdk/docs/programming-guide"""
    pass

class VehicleNotFound(Exception):
    """Could not find a Supercar"""
    pass

class DuplicateScanWarning(Warning):
    """The map has already been scanned, but scan has been called anyway. This is not dangerous, but unneccessary"""
    pass