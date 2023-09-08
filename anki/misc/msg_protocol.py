from typing import Union
from . import const
from ..errors import * 

def assemble_packet(
        msgType : Union[bytes,bytearray],
        payload : Union[str,bytes,bytearray]
    ) -> bytes:
    try:
        msgType_bytes = bytes(msgType)
    except TypeError as e:
        raise TypeError(
            f"Could not cast msgType to bytes. Should be either bytes or bytearray, was {type(msgType)}"
            ) from e
    if not (
        msgType_bytes in const.ControllerMsg.__dict__.values() 
        or msgType_bytes in const.VehicleMsg.__dict__.values()
        ): 
        # Only allow for msgTypes specified in const.ControllerMsg or const.VehicleMsg
        raise ValueError(f"msgType has to be a type specified in const.ControllerMsg or const.VehicleMsg (latter is discouraged). You entered {msgType_bytes}")
        pass

    try:
        if isinstance(payload,str): 
            payload_bytes = payload.encode()
            pass
        else: 
            payload_bytes = bytes(payload)
            pass
    except TypeError as e:
        raise TypeError(
            f"Could not cast payload to bytes. Should be either str, bytes or bytesarray, was {type(payload)}"
        )

    size : int = len(msgType) + len(payload_bytes)
    byteSize = size.to_bytes(1,"little",signed=False)

    return byteSize + msgType + payload_bytes
    pass

def disassemble_packet(
        packet : Union[bytes,bytearray]
    ) -> tuple[int,bytes]:
    try:
        bytes_packet = bytes(packet)
    except TypeError as e:
        raise TypeError(f"Parameter packet could not be cast to bytes, should be either bytes or bytesarray, was {type(packet)}") from e

    ####
    packageSize = bytes_packet[0] # Single indexes of bytes are ints
    actualSize = len(bytes_packet[1:])
    # Security check
    if actualSize != packageSize:
        raise MalformedPacketWarning(f"Package Size did not match the actual size of the packet ({packageSize} != {actualSize})")
        pass

    msgType = bytes_packet[1]
    payload = bytes_packet[2:]
    if len(payload) > const.MAX_PACKET_PAYLOAD_SIZE:
        raise MalformedPacketWarning(f"Payload is too large. Has to be <= {const.MAX_PACKET_PAYLOAD_SIZE}, is {len(payload)}")
        pass

    return msgType, payload
    pass