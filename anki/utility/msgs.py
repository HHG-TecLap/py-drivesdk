from .msg_protocol import *
from . import const
import struct

def set_speed_pkg(speed : int, accel : int = 500):
    speedBytes = speed.to_bytes(2,"little",signed=True)
    accelBytes = accel.to_bytes(2,"little",signed=True)

    return assemble_packet(const.ControllerMsg.SET_SPEED,speedBytes+accelBytes)
    pass

def set_sdk_pkg(state : bool, flags : int = 0):
    stateBytes = b"\xff" if state else b"\x00"
    flagBytes = flags.to_bytes(1,"little",signed=False)

    return assemble_packet(const.ControllerMsg.SET_SDK,stateBytes+flagBytes)
    pass

def turn_180_pkg(type : int, trigger : int):
    return assemble_packet(const.ControllerMsg.TURN_180,type.to_bytes(1,"little",signed=False) + trigger.to_bytes(1,"little",signed=False))
    pass

def change_lane_pkg(roadCenterOffset : float, horizontalSpeed : int = 300, horizontalAcceleration : int = 300, _hopIntent : int = 0x0, _tag : int = 0x0):

    return assemble_packet(const.ControllerMsg.CHANGE_LANE,struct.pack("<HHfBB",horizontalSpeed,horizontalAcceleration,roadCenterOffset,_hopIntent,_tag))
    pass

def set_light_pkg(light : int):
    return assemble_packet(const.ControllerMsg.SET_LIGHTS,light.to_bytes(1,"little",signed=False))
    pass

def light_pattern_pkg(r : int,g : int,b : int):
    return assemble_packet(const.ControllerMsg.LIGHT_PATTERN,struct.pack("<BBBBBBBBBBBBBBBB",3,0,0,r,r,0,3,0,g,g,0,2,0,b,b,0))
    pass

def disassemble_track_update(payload : bytes) -> tuple[int,int,float,int,int]:
    return struct.unpack_from("<BBfHB", payload)
    pass

def disassemble_track_change(payload : bytes) -> tuple[int,int,float,int,int,int,int,int,int,int,int,int]:
    """HA! You think this is useful! No! The first two values are always 0! And those are the road piece and the previous road piece! THIS IS HORRIBLE! WHY DOES THERE HAVE TO BE SUCH LACK OF DOCUMENTATION?! I HATE IT!"""

    road_piece, prev_road_piece, road_offset, last_received_lane_change_id, last_executed_lane_change_id, last_desired_lane_change_speed, ave_follow_line_drift_pixels, had_lane_change, uphill_counter, downhill_counter, left_wheel_dist, right_wheel_dist = struct.unpack_from("<bbfBBHbBBBBB",payload)

    return (
        road_piece, 
        prev_road_piece, 
        road_offset, 
        last_received_lane_change_id, 
        last_executed_lane_change_id, 
        last_desired_lane_change_speed, 
        ave_follow_line_drift_pixels, 
        had_lane_change, 
        uphill_counter, 
        downhill_counter, 
        left_wheel_dist, 
        right_wheel_dist
    )
    pass