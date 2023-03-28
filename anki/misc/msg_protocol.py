from typing import Union
from . import const
from ..errors import * 

def assemble_packet(
        msgType : Union[bytes,bytearray],
        payload : Union[str,bytes,bytearray]
    ) -> bytes:
    if isinstance(msgType, bytearray):
        msgType = bytes(msgType)
        pass
    msgType : bytes
    if not isinstance(msgType,bytes): 
        raise TypeError(f"msgType has to be a bytes or bytesarray type, not {type(msgType)}")
        pass
    elif not (
        msgType in const.ControllerMsg.__dict__.values() 
        or msgType in const.VehicleMsg.__dict__.values()
        ): 
        # Only allow for msgTypes specified in const.ControllerMsg or const.VehicleMsg
        raise ValueError(f"msgType has to be a type specified in const.ControllerMsg or const.VehicleMsg (latter is discouraged). You entered {msgType}")
        pass

    if isinstance(payload,str): payload = payload.encode()
    elif isinstance(payload,bytearray): payload = bytes(payload)
    payload: bytes # Explicit typing for linter clarity
    if not isinstance(payload,bytes): # If not a bytes object, raise TypeError
        raise TypeError(f"payload has to be bytes, str, or bytesarray object, not {type(msgType)}")
        pass

    size : int[0,256] = len(msgType) + len(payload)
    byteSize = size.to_bytes(1,"little",signed=False)

    return byteSize + msgType + payload
    pass

def disassemble_packet(
        packet : Union[bytes,bytearray]
    ) -> tuple[int,bytes]:
    if isinstance(packet,bytearray):
        packet = bytes(packet)
        pass
    packet : bytes
    if not isinstance(packet,bytes):
        raise TypeError(f"package has to either be bytes or bytearray object. Was {type(packet)}")
        pass

    ####
    packageSize = packet[0] # Single indexes of bytes are ints
    actualSize = len(packet[1:])
    # Security check
    if actualSize != packageSize:
        raise MalformedPacketWarning(f"Package Size did not match the actual size of the packet ({packageSize} != {actualSize})")
        pass

    msgType = packet[1]
    payload = packet[2:]
    if len(payload) > const.MAX_PACKET_PAYLOAD_SIZE:
        raise MalformedPacketWarning(f"Payload is too large. Has to be <= {const.MAX_PACKET_PAYLOAD_SIZE}, is {len(payload)}")
        pass

    return msgType, payload
    pass