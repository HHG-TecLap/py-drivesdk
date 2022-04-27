from typing import Callable, Optional
import bleak, asyncio
from bleak.backends.device import BLEDevice
import dataclasses

from .utility import util

from .msgs import *
from .utility.track_pieces import TrackPiece
from .utility import const
from .utility.lanes import Lane3, Lane4, _Lane
from . import errors

def interpretLocalName(name : str):
    if name is None or len(name) < 1: # Fix some issues that might occur
        raise ValueError("Name was empty")
        pass
    nameBytes = name.encode("utf-8")
    vehicleState = nameBytes[0]
    version = int.from_bytes(nameBytes[1:3],"little",signed=False)
    vehicleName = nameBytes[8:].decode("utf-8")

    return VehicleState.from_int(vehicleState), version, vehicleName
    pass

@dataclasses.dataclass(frozen=True)
class VehicleState:
    full_battery : bool
    low_battery : bool
    charging : bool

    @classmethod
    def from_int(cls, state : int):
        full     = bool(state & (1 << const.VehicleBattery.FULL_BATTERY))
        low      = bool(state & (1 << const.VehicleBattery.LOW_BATTERY))
        charging = bool(state & (1 << const.VehicleBattery.ON_CHARGER))

        return cls(full,low,charging)
        pass
    pass

class Lights:
    HEADLIGHTS = 0
    BRAKELIGHTS = 1
    FRONTLIGHTS = 2
    ENGINELIGHTS = 3

class Vehicle:
    __slots__ = ["__client__","_current_track_piece","_is_connected","_road_offset","on_track_piece_change","_track_piece_future","_position","_map","__read_chara__","__write_chara__"]
    def __init__(self, device : BLEDevice, client : bleak.BleakClient = None):
        self.__client__ = client if client is not None else bleak.BleakClient(device)

        self._current_track_piece : TrackPiece = None
        """Do not use! This can only show the last position for... reasons"""
        self._is_connected = False
        self._road_offset : float = ...
        self._map : Optional[list[TrackPiece]] = None
        self._position : Optional[int] = None

        self.on_track_piece_change : Callable = lambda: None # Set a dummy function by default
        self._track_piece_future = asyncio.Future()
        pass

    def __notify_handler__(self,handler,data : bytearray):
        msg_type, payload = util.disassemblePacket(data)
        if msg_type == const.VehicleMsg.TRACK_PIECE_UPDATE:
            loc, piece, offset, speed, clockwise = disassemble_track_update(payload)

            self._road_offset = offset
            piece_obj = TrackPiece(loc,piece,clockwise)

            self._current_track_piece = piece_obj
            pass
        elif msg_type == const.VehicleMsg.TRACK_PIECE_CHANGE:
            if None not in (self._position, self._map):
                self._position += 1
                self._position %= len(self._map)
                track_piece = self.current_track_piece # This is very hacky! (And also doesn't ~~quite~~ work)
                pass
            else:
                track_piece = self._current_track_piece
                pass

            self._track_piece_future.set_result(None)
            self._track_piece_future = asyncio.Future()
            self.on_track_piece_change()
            pass
        pass

    async def __send_package__(self, payload : bytes):
        await self.__client__.write_gatt_char(self.__write_chara__,payload)
        pass

    async def wait_for_track_change(self) -> Optional[TrackPiece]:
        await self._track_piece_future
        return self.current_track_piece
        pass

    async def connect(self):
        """Connect to the Supercar\n
        Don't forget to call Vehicle.disconnect() on program exit!"""
        await self.__client__.connect()
        # Get service and characteristics
        services = await self.__client__.get_services()
        anki_service = services.get_service(const.SERVICE_UUID)
        read   = anki_service.get_characteristic(const.READ_CHAR_UUID)
        write  = anki_service.get_characteristic(const.WRITE_CHAR_UUID)

        await self.__client__.write_gatt_char(write,setSdkPkg(True,0x1)) # Enable SDK mode
        await self.__client__.start_notify(read,self.__notify_handler__) # Start Notifier for data handling

        self.__read_chara__ = read
        self.__write_chara__= write

        self._is_connected = True
        pass

    async def disconnect(self) -> bool:
        """Disconnect from the Supercar\nNOTE: Always do this on program exit!"""
        self._is_connected = not await self.__client__.disconnect()
        if self._is_connected:
            raise errors.Di
        
        return self._is_connected
        pass


    async def setSpeed(self, speed : int, acceleration : int = 500):
        """Set the speed of the Supercar in mm/s"""
        await self.__send_package__(setSpeedPkg(speed,acceleration))
        pass

    async def stop(self):
        """Stops the Supercar"""
        await self.setSpeed(0,1000)
        pass

    async def change_lane(self, lane : _Lane, horizontalSpeed : int = 300, horizontalAcceleration : int = 300, *, _hopIntent : int = 0x0, _tag : int = 0x0):
        await self.change_position(lane.lane_position,horizontalSpeed,horizontalAcceleration,_hopIntent=_hopIntent,_tag=_tag)
        pass

    async def change_position(self, roadCenterOffset : float, horizontalSpeed : int = 300, horizontalAcceleration : int = 300, *, _hopIntent : int = 0x0, _tag : int = 0x0):
        await self.__send_package__(changeLanePkg(roadCenterOffset,horizontalSpeed,horizontalAcceleration,_hopIntent,_tag))
        pass

    async def turn(self, type : int = 3, trigger : int = 0):
        """NOTE: Does not function properly"""
        await self.__send_package__(turn180Pkg(type,trigger))
        pass

    async def setLights(self,light : int):
        """NOTE: Does not seem to work correctly. Likely an issue with the vehicles"""
        raise DeprecationWarning("This function is deprecated and does not work due to a bug in the vehicle computer.")

        await self.__send_package__(setLightPkg(light))
        pass

    async def setLightPattern(self, r : int, g : int, b : int):
        """NOTE: Does not seem to work correctly\n
        NOTE: Needs further investigation (might not have all arguments covered)"""
        raise DeprecationWarning("This function is deprecated and does not work due to a bug in the vehicle computer.")

        await self.__send_package__(lightPatternPkg(r,g,b))
        pass

    def get_lane(self, mode : type[_Lane]) -> _Lane:
        return mode.get_closest_lane(self._road_offset)
        pass

    @property
    def is_connected(self) -> bool:
        return self._is_connected
        pass

    @property
    def current_track_piece(self) -> TrackPiece:
        if None in (self.map, self.map_position):
            return None
            pass
        return self.map[self.map_position]
        pass

    @property
    def map(self) -> tuple[TrackPiece]:
        return tuple(self._map) if self._map is not None else None
        pass

    @property
    def map_position(self) -> int:
        return self._position
        pass

    @property
    def road_offset(self) -> float:
        return self._road_offset
        pass

    @property
    def current_lane3(self) -> Lane3:
        return self.get_lane(Lane3)
        pass

    @property
    def current_lane4(self) -> Lane4:
        return self.get_lane(Lane4)
        pass
    pass