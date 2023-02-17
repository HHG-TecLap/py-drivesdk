from warnings import warn

from typing import Callable, Optional
import bleak, asyncio
from bleak.backends.device import BLEDevice
import dataclasses
from bleak.exc import BleakDBusError

from ..utility import util

from ..msgs import *
from ..utility.track_pieces import TrackPiece, TrackPieceTypes
from ..utility import const
from ..utility.lanes import Lane3, Lane4, _Lane
from .. import errors

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .controller import Controller
    pass


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
    """Represents the state of a supercar"""
    full_battery : bool
    low_battery : bool
    charging : bool

    @classmethod
    def from_int(cls, state : int):
        """Constructs a :class:`VehicleState` from an integer representation
        
        :param state: :class:`int`
            The integer state passed by the discovery process
        
        Returns
        -------
        :class:`VehicleState`
        The new :class:`VehicleState` instance"""
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
    """This class represents a supercar. With it you can control all functions of said supercar.

    
    :param id: :class:`int`
        The id of the :class:`Vehicle` object
    :param device: :class:`bleak.BLEDevice`
        The BLE device representing the supercar
    :param client: :class:`Optional[bleak.BleakClient]` 
        A client wrapper around the BLE device
    
    .. note::
        You should not create this class manually, use one of the connect methods in the :class:`Controller`.
    """

    __slots__ = ("_client","_current_track_piece","_is_connected","_road_offset","_speed","on_track_piece_change","_track_piece_future","_position","_map","_read_chara","_write_chara", "_id","_track_piece_watchers","_pong_watchers","_controller")
    def __init__(self, id : int, device : BLEDevice, client : bleak.BleakClient = None, controller : "Controller" = None):
        self._client = client if client is not None else bleak.BleakClient(device)

        self._id : int = id
        self._current_track_piece : TrackPiece = None
        """Do not use! This can only show the last position for... reasons"""
        self._is_connected = False
        self._road_offset : float = ...
        self._speed : int = 0
        self._map : Optional[list[TrackPiece]] = None
        self._position : Optional[int] = None

        self.on_track_piece_change : Callable = lambda: None # Set a dummy function by default
        self._track_piece_future = asyncio.Future()
        self._track_piece_watchers = []
        self._pong_watchers = []
        self._controller = controller
        pass

    def __notify_handler__(self,handler,data : bytearray):
        """An internal handler function that gets called on a notify receive"""
        msg_type, payload = util.disassemblePacket(data)
        if msg_type == const.VehicleMsg.TRACK_PIECE_UPDATE:
            # This gets called when part-way along a track piece (sometimes)
            loc, piece, offset, speed, clockwise = disassembleTrackUpdate(payload)

            # Update internal variables when new info available
            self._road_offset = offset
            self._speed = speed

            # Post a warning when TrackPiece creation failed (but not an error)
            try:
                piece_obj = TrackPiece.from_raw(loc,piece,clockwise)
            except ValueError:
                warn(f"A TrackPiece value received from the vehicle could not be decoded. If you are running a scan, this will break it. Received: {piece}",errors.TrackPieceDecodeWarning)
                return
                pass

            self._current_track_piece = piece_obj # Update the internal track object
            pass
        elif msg_type == const.VehicleMsg.TRACK_PIECE_CHANGE:
            uphill_count, downhill_count = disassembleTrackChange(payload)[8:10]
            print("Vehicle uphill/downhill:",uphill_count,downhill_count)
            if None not in (self._position, self._map): # If there was a scan & align already
                self._position += 1
                self._position %= len(self._map)
                track_piece = self.current_track_piece # This is very hacky! (And also doesn't ~~quite~~ work)
                if self._current_track_piece.type is TrackPieceTypes.START:
                    self._position = 1
                pass
            else:
                track_piece = self._current_track_piece
                pass

            self._track_piece_future.set_result(None) # Complete internal future when on new track piece. This is used in wait_for_track_change
            self._track_piece_future = asyncio.Future() # Create new future since the old one is now done
            self.on_track_piece_change() # Call the track piece event handle
            for func in self._track_piece_watchers:
                func()
                pass
            pass
        elif msg_type == const.VehicleMsg.PONG:
            for func in self._pong_watchers:
                func()
                pass
            pass
        elif msg_type == const.VehicleMsg.CHARGER_INFO:
            unknown, onCharger, loading, full = disassembleChargerInfo(payload)
            print(f'unknown: {unknown}, onCharger: {onCharger}, loading: {loading}, full: {full}')
        pass

    async def __send_package__(self, payload : bytes):
        """Send a payload to the supercar"""
        try:
            await self._client.write_gatt_char(self._write_chara,payload)
        except OSError:
            raise DisconnectedVehiclePackage("A command was sent to a vehicle that is already disconnected")
            pass
        pass

    async def wait_for_track_change(self) -> Optional[TrackPiece]:
        """Waits until the current track piece changes.
        
        Returns
        -------
        :class:`TrackPiece`
            The new track piece. `None` if :func:`Vehicle.map` is None
            (for example if the map has not been scanned yet)
        """
        await self._track_piece_future # Wait on a new track piece (See __notify_handler__)
        return self.current_track_piece
        pass

    async def connect(self):
        """Connect to the Supercar
        **Don't forget to call Vehicle.disconnect on program exit!**
        
        Raises
        ------
        :class:`ConnectionTimedoutException`
            The connection attempt to the supercar did not succeed within the set timeout
        :class:`ConnectionDatabusException`
            A databus error occured whilst connecting to the supercar
        :class:`ConnectionFailedException`
            A generic error occured whilst connection to the supercar
        """
        try:
            if not (await self._client.connect()): raise bleak.BleakError # Handle a failed connect the same way as a BleakError
            pass
        # Catch a bunch of errors occuring on connection
        except BleakDBusError:
            raise errors.ConnectionDatabusException(
                "An attempt to connect to the vehicle failed. This can occur sometimes and is usually not an error in your code."
            )
        except bleak.BleakError:
            raise errors.ConnectionFailedException(
                "An attempt to connect to the vehicle failed. This is usually not associated with your code."
            )
        except asyncio.TimeoutError:
            raise errors.ConnectionTimedoutException(
                "An attempt to connect to the vehicle timed out. Make sure the car is actually disconnected."
            )
        
        # Get service and characteristics
        services = await self._client.get_services()
        anki_service = services.get_service(const.SERVICE_UUID)
        read   = anki_service.get_characteristic(const.READ_CHAR_UUID)  
        write  = anki_service.get_characteristic(const.WRITE_CHAR_UUID) 

        await self._client.write_gatt_char(write,setSdkPkg(True,0x1)) # Enable SDK mode
        await self._client.start_notify(read,self.__notify_handler__) # Start Notifier for data handling

        self._read_chara = read
        self._write_chara= write

        self._is_connected = True
        pass

    async def disconnect(self) -> bool:
        """Disconnect from the Supercar

        .. note::
            Remember to execute this for every connected :class:`Vehicle` once the program exits.
            Not doing so will result in your supercars not connecting sometimes as they still think they are connected.

        Returns
        -------
        :class:`bool`
        The connection state of the :class:`Vehicle` instance. This should always be `False`

        Raises
        ------
        :class:`DisconnectTimedoutException`
            The attempt to disconnect from the supercar timed out
        :class:`DisconnectFailedException`
            The attempt to disconnect from the supercar failed for an unspecified reason
        """
        try:
            self._is_connected = not await self._client.disconnect()
        except asyncio.TimeoutError:
            raise errors.DisconnectTimedoutException("The attempt to disconnect from the vehicle timed out.")
        if self._is_connected:
            raise errors.DisconnectFailedException("The attempt to disconnect the vehicle failed.")
        
        if not self._is_connected and self._controller is not None:
            self._controller.vehicles.remove(self)
            pass

        return self._is_connected
        pass


    async def setSpeed(self, speed : int, acceleration : int = 500):
        """Set the speed of the Supercar in mm/s

        :param speed: :class:`int`
            The speed in mm/s
        :param acceleration: :class:`Optional[int]`
            The acceleration in mm/s²
        """
        await self.__send_package__(setSpeedPkg(speed,acceleration))
        self._speed = speed # Update the internal speed as well (even though it technically is an overestimate as we need to accelerate first)
        pass

    async def stop(self):
        """Stops the Supercar"""
        await self.setSpeed(0, 600) # stop = 0 speed
        pass

    async def changeLane(self, lane : _Lane, horizontalSpeed : int = 300, horizontalAcceleration : int = 300, *, _hopIntent : int = 0x0, _tag : int = 0x0):
        """Change to a desired lane

        :param lane: :class:`_Lane` 
            The lane to move into. These may be :class:`Lane3` or :class:`Lane4`
        :param horizontalSpeed: :class:`Optional[int]`
            The speed the vehicle will move along the track at in mm/s
        :param horizontalAcceleration: :class:`Optional[int]`
            The acceleration in mm/s² the vehicle will move horizontally with 
        """
        await self.changePosition(lane.lane_position,horizontalSpeed,horizontalAcceleration,_hopIntent=_hopIntent,_tag=_tag) # changeLane is just changePosition but user friendly
        pass

    async def changePosition(self, roadCenterOffset : float, horizontalSpeed : int = 300, horizontalAcceleration : int = 300, *, _hopIntent : int = 0x0, _tag : int = 0x0):
        """Change to a position offset from the track centre
        
        :param roadCenterOffset: :class:`float`
            The target offset from the centre of the track piece in mm
        :param horizontalSpeed: :class:`int`
            The speed the vehicle will move along the track at in mm/s
        :param horizontalAcceleration: :class:`int`
            The acceleration in mm/s² the vehicle will move horizontally with 
        """
        await self.__send_package__(changeLanePkg(roadCenterOffset,horizontalSpeed,horizontalAcceleration,_hopIntent,_tag))
        pass

    async def turn(self, type : int = 3, trigger : int = 0): # type and trigger don't work correcty
        """
        .. warning::
            This does not yet function properly. It is advised not to use this method
        """
        await self.__send_package__(turn180Pkg(type,trigger))
        pass

    async def setLights(self,light : int):
        """Set the lights of the vehicle in accordance with a bitmask

        .. warning::
            This function is deprecated due to not functioning properly. 
            It will not execute.
        """
        raise DeprecationWarning("This function is deprecated and does not work due to a bug in the vehicle computer.")

        await self.__send_package__(setLightPkg(light))
        pass

    async def setLightPattern(self, r : int, g : int, b : int):
        """Set the engine light (the big one) at the top of the vehicle

        .. warning::
            This function is deprecated due to a hardware bug causing it not to function. 
            It will not execute.
        """
        raise DeprecationWarning("This function is deprecated and does not work due to a bug in the vehicle computer.")

        await self.__send_package__(lightPatternPkg(r,g,b))
        pass

    def getLane(self, mode : type[_Lane]) -> Optional[_Lane]:
        """Get the current lane given a specific lane type

        :param mode: :class:`_Lane` 
            A class such as :class:`Lane3` or :class:`Lane4` inheriting from :class:`_Lane`. This is the lane system being used
        
        Returns
        -------
        :class:`Optional[_Lane]`
            The lane the vehicle is on. This may be none if no lane information is available 
            (such as at the start of the program, when the vehicles haven't moved much)
        """
        if self._road_offset is ...:
            return None
        else:
            return mode.getClosestLane(self._road_offset)
        pass
    async def align(self, speed : int = 300):
        """Align to the start piece. This only works if the map is already scanned in

        :param speed: :class:`int`
            The speed the vehicle should travel at during alignment
        """
        await self.setSpeed(speed)
        while self._current_track_piece.type is TrackPieceTypes.FINISH:
            # Waits until the previous track piece was FINISH.
            # This means the current position is START
            await self.wait_for_track_change()
            pass

        self._position = 0 # Vehicle is now at START which is always 0

        await self.stop()
        pass
    
    def trackPieceChange(self, func):
        """
        A decorator marking a function to be executed when the supercar drives onto a new track piece

        :param func: :class:`function`
            The listening function
        
        Returns
        -------
        :class:`function`
            The function that was passed in
        """
        self._track_piece_watchers.append(func)
        return func
        pass

    def removeTrackPieceWatcher(self, func):
        """
        Remove a track piece event handler added by :func:`Vehicle.trackPieceChange`

        :param func: :class:`function`
            The function to remove as an event handler
        
        Raises
        ------
        :class:`ValueError`
            The function passed is not an event handler
        """
        self._track_piece_watchers.remove(func)
        pass

    async def ping(self):
        await self.__send_package__(util.const.ControllerMsg.PING)
        pass

    def pong(self, func):
        """
        A decorator marking an function to be executed when the supercar responds to a Ping

        :param func: :class:`function`
            The function to mark as a listener
        
        Returns
        -------
        :class:`function`
            The function being passed in
        """
        self._pong_watchers.append(func)
        return func
        pass

    @property
    def is_connected(self) -> bool:
        """
        `True` if the vehicle is currently connected
        """
        return self._is_connected
        pass

    @property
    def current_track_piece(self) -> TrackPiece:
        """
        The :class:`TrackPiece` the vehicle is currently located at

        .. note::
            This will return :class:`None` if either scan or align is not completed
        """
        if None in (self.map, self.map_position): # If no scan or align not complete, we can't find the track piece
            return None
            pass
        return self.map[self.map_position]
        pass

    @property
    def map(self) -> tuple[TrackPiece]:
        """
        The map the :class:`Vehicle` instance is using. 
        This is :class:`None` if the :class:`Vehicle` does not have a map supplied.
        """
        return tuple(self._map) if self._map is not None else None
        pass

    @property
    def map_position(self) -> int:
        """
        The position of the :class:`Vehicle` instance on the map.
        This is :class:`None` if :func:`Vehicle.align` has not yet been called.
        """
        return self._position
        pass

    @property
    def road_offset(self) -> float:
        """
        The offset from the road centre.
        This is :class:`None` if the supercar did not send any information yet. (Such as when it hasn't moved much)
        """
        return self._road_offset
        pass

    @property
    def speed(self) -> int:
        """
        The speed of the supercar in mm/s.
        This is :class:`None` if the supercar has not moved or :func:`Vehicle.setSpeed` hasn't been called yet.
        """
        return self._speed
        pass

    @property
    def current_lane3(self) -> Optional[Lane3]:
        """
        Short-hand for 
        
        .. code-block:: python
            
            Vehicle.getLane(Lane3)
        """
        return self.getLane(Lane3)
        pass

    @property
    def current_lane4(self) -> Optional[Lane4]:
        """
        Short-hand for 
        
        .. code-block:: python
            
            Vehicle.getLane(Lane4)
        """
        return self.getLane(Lane4)
        pass

    @property
    def id(self) -> int:
        """
        The id of the :class:`Vehicle` instance. This is set during initialisation of the object.
        """
        return self._id
        pass
    pass
