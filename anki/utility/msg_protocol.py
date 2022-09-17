from typing import Union
from . import const
from ..errors import * 

def assemble_packet(msgType : Union[bytes,bytearray],payload : Union[str,bytes,bytearray]) -> bytes:
    if isinstance(msgType, bytearray): # Convert bytearray to bytes
        msgType = bytes(msgType)
        pass
    msgType : bytes
    if not isinstance(msgType,bytes): # Raise TypeError if msgType is not a bytes object
        raise TypeError(f"msgType has to be a bytes or bytesarray type, not {type(msgType)}")
        pass
    elif not (msgType in const.ControllerMsg.__dict__.values() or msgType in const.VehicleMsg.__dict__.values()): # Only allow for msgTypes specified in const.ControllerMsg or const.VehicleMsg
        raise ValueError(f"msgType has to be a type specified in const.ControllerMsg or const.VehicleMsg (latter is discouraged). You entered {msgType}")
        pass

    if isinstance(payload,str): payload = payload.encode() # Convert str to bytes
    elif isinstance(payload,bytearray): payload = bytes(payload) # Convert bytearray to bytes
    payload : bytes
    if not isinstance(payload,bytes): # If not a bytes object, raise TypeError
        raise TypeError(f"payload has to be bytes, str, or bytesarray object, not {type(msgType)}")
        pass

    # Actual code
    size : int[0,256] = len(msgType) + len(payload)
    byteSize = size.to_bytes(1,"little",signed=False)

    return byteSize + msgType + payload
    pass

def disassemble_packet(packet : Union[bytes,bytearray]) -> tuple[bytes,bytes]:
    if isinstance(packet,bytearray): # Convert bytearray to bytes
        packet = bytes(packet)
        pass
    packet : bytes
    if not isinstance(packet,bytes): # Raise TypeError if package is not a bytes object.
        raise TypeError(f"package has to either be bytes or bytearray object. Was {type(packet)}")
        pass

    ####
    packageSize = packet[0] # First byte is size of packet
    actualSize = len(packet[1:]) # Check for packet size regardless for security reasons
    if actualSize != packageSize: # Raise MalformedPacketWarning if size does not match
        raise MalformedPacketWarning(f"Package Size did not match the actual size of the packet ({packageSize} != {actualSize})")
        pass

    msgType = packet[1] # Msg type is second byte
    payload = packet[2:] # Rest is just the payload
    if len(payload) > const.MAX_PACKET_PAYLOAD_SIZE:
        raise MalformedPacketWarning(f"Payload is too large. Has to be <= {const.MAX_PACKET_PAYLOAD_SIZE}, is {len(payload)}")
        pass

    return msgType, payload
    pass