from .msg_protocol import assemble_packet
from . import const
import struct
from typing import Literal


def set_speed_pkg(speed: int, accel: int=500):
    speedBytes = speed.to_bytes(2, "little", signed=True)
    accelBytes = accel.to_bytes(2, "little", signed=True)

    return assemble_packet(
        const.ControllerMsg.SET_SPEED,
        speedBytes + accelBytes
    )
    pass


def set_sdk_pkg(state: bool, flags: int=0):
    state_bytes = b"\xff" if state else b"\x00"
    flag_bytes = flags.to_bytes(1, "little", signed=False)

    return assemble_packet(
        const.ControllerMsg.SET_SDK,
        state_bytes + flag_bytes
    )
    pass


def turn_180_pkg(type: int, trigger: int):
    return assemble_packet(
        const.ControllerMsg.TURN_180,
        type.to_bytes(1, "little", signed=False)
        + trigger.to_bytes(1, "little", signed=False)
    )
    pass


def change_lane_pkg(
        roadCenterOffset: float,
        horizontalSpeed: int=300,
        horizontalAcceleration: int=300,
        _hopIntent: int=0x0,
        _tag: int=0x0
):
    return assemble_packet(
        const.ControllerMsg.CHANGE_LANE,
        struct.pack(
            "<HHfBB",
            horizontalSpeed,
            horizontalAcceleration,
            roadCenterOffset,
            _hopIntent,
            _tag
        )
    )
    pass


def set_light_pkg(light: int):
    return assemble_packet(
        const.ControllerMsg.SET_LIGHTS,
        light.to_bytes(1, "little", signed=False)
    )
    pass


def light_pattern_pkg(r: int, g: int, b: int):
    return assemble_packet(
        const.ControllerMsg.LIGHT_PATTERN,
        struct.pack(
            "<BBBBBBBBBBBBBBBB",
            3, 0, 0,
            r, r,
            0, 3, 0,
            g, g,
            0, 2, 0,
            b, b,
            0
        )
    )
    pass

def ping_pkg():
    return assemble_packet(
        const.ControllerMsg.PING,
        b""
    )


def disassemble_track_update(
        payload: bytes
) -> tuple[int, int, float, int, int]:
    return struct.unpack_from("<BBfHB", payload)  # type: ignore
    pass


def disassemble_track_change(
        payload: bytes
) -> tuple[
        Literal[0],
        Literal[0],
        float,
        int,
        int,
        int,
        int,
        int,
        int,
        int,
        int,
        int
]:
    """
    HA! You think this is useful! No!
    The first two values are always 0!
    And those are the road piece and the previous road piece!
    THIS IS HORRIBLE!
    WHY DOES THERE HAVE TO BE SUCH LACK OF DOCUMENTATION?!
    I HATE IT!

    Returning values are as follows:
    
    1. "road_piece"
        the current road piece (always 0 because fuck you that's why)
    2. "prev_road_piece"
        the previous road piece (always 0 because see above)
    3. "road_offset"
        offset from the centre of the road in mm
    4. "last_received_lane_change_id"
        the id of the last received lane change (that system has ids apparently)
    5. "last_executed_lane_change_id"
        the id of the last executed lane change (I think. Haven't actually tested it)
    6. "last_desired_lane_change_speed"
        the desired speed of the last executed lane speed
    7. "ave_follow_line_drift_pixels"
        I don't fucking know
    8. "had_lane_change"
        If there was a lane change on the last track piece... Probably.
    9. "uphill_counter"
        Something to do with the incline/height of the track
    10. "downhill_counter"
        See above
    11. "left_wheel_dist"
        Probably something like the distance of the left wheel from the track centre.
        Useful for curve detection probably.
    12. "right_wheel_dist"
        See above
    """

    return struct.unpack_from("<bbfBBHbBBBBB", payload)  # type: ignore
    pass


def disassemble_charger_info(
        payload: bytes
) -> tuple[bool, bool, bool, bool]:
    return struct.unpack_from('<????', payload)  # type: ignore
