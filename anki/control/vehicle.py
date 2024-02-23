from ..misc.deprecated_alias import AliasMeta, deprecated_alias
from warnings import warn
from enum import IntEnum

from typing import Callable, Optional
import bleak
import asyncio
from bleak.backends.device import BLEDevice
import dataclasses
from bleak.exc import BleakDBusError, BleakError

from ..misc import msg_protocol

from ..misc.msgs import (
    disassemble_charger_info,
    disassemble_track_update,
    disassemble_track_change,
    set_sdk_pkg,
    set_speed_pkg,
    change_lane_pkg,
    turn_180_pkg,
)
from ..misc.track_pieces import TrackPiece, TrackPieceType
from ..misc import const
from ..misc.lanes import Lane3, Lane4, BaseLane, _Lane
from .. import errors

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .controller import Controller
    pass

_Callback = Callable[[], None]


def interpret_local_name(name: str|None):
    # Get the state of the vehicle from the local name
    if name is None or len(name) < 1:  # Fix some issues that might occur
        raise ValueError("Name was empty")
        pass
    nameBytes = name.encode("utf-8")
    vehicleState = nameBytes[0]
    version = int.from_bytes(nameBytes[1:3], "little", signed=False)
    vehicleName = nameBytes[8:].decode("utf-8")

    return BatteryState.from_int(vehicleState), version, vehicleName
    pass


def _call_all_soon(funcs, *args):
    # Registers everything in funcs to be called soon with *args
    for f in funcs:
        asyncio.get_running_loop().call_soon(f, *args)


@dataclasses.dataclass(frozen=True)
class BatteryState:
    """Represents the state of a supercar"""
    full_battery: bool
    low_battery: bool|None
    on_charger: bool
    charging: bool|None = None

    @classmethod
    def from_int(cls, state: int):
        """Constructs a :class:`BatteryState` from an integer representation
        
        :param state: :class:`int`
            The integer state passed by the discovery process
        
        Returns
        -------
        :class:`BatteryState`
        The new :class:`BatteryState` instance
        """
        full = bool(state & (1 << const.VehicleBattery.FULL_BATTERY))
        low = bool(state & (1 << const.VehicleBattery.LOW_BATTERY))
        on_charger = bool(state & (1 << const.VehicleBattery.ON_CHARGER))

        return cls(full, low, on_charger)
        pass

    @classmethod
    def from_charger_info(cls, payload: bytes):
        """
        Constructs a :class:`BatteryState` instance from a CHARGER_INFO message.

        :param payload: :class:`bytes`
            The payload of the CHARGER_INFO message
        
        Returns
        -------
        :class:`BatteryState`
        The new :class:`BatteryState` instance
        """
        _, on_charger, charging, full = disassemble_charger_info(payload)
        return cls(full, None, on_charger, charging)
        pass
    pass


class Lights(IntEnum):
    HEADLIGHTS = 0
    BRAKELIGHTS = 1
    FRONTLIGHTS = 2
    ENGINELIGHTS = 3


class Vehicle(metaclass=AliasMeta):
    """This class represents a supercar. With it you can control all functions of said supercar.

    
    :param id: :class:`int`
        The id of the :class:`Vehicle` object
    :param device: :class:`bleak.BLEDevice`
        The BLE device representing the supercar
    :param client: :class:`Optional[bleak.BleakClient]`
        A client wrapper around the BLE device
    
    .. note::
        You should not create this class manually,
        use one of the connect methods in the :class:`Controller`.
    """

    AUTOMATIC_PING_CONTROL = {
        "interval": 10,
        "timeout": 10,
        "max_timeouts": 2
    }

    __slots__ = (
        "_client",
        "_current_track_piece",
        "_is_connected",
        "_road_offset",
        "_speed",
        "on_track_piece_change",
        "_track_piece_future",
        "_position",
        "_map",
        "_read_chara",
        "_write_chara",
        "_id",
        "_track_piece_watchers",
        "_pong_watchers",
        "_delocal_watchers",
        "_battery_watchers",
        "_controller",
        "_ping_task",
        "_battery"
    )
    
    def __init__(
            self,
            id: int,
            device: BLEDevice,
            client: bleak.BleakClient|None=None,
            controller: Optional["Controller"]=None,  # Inconsistent, but fixes failing docs
            *,
            battery: BatteryState
    ):
        self._client = client if client is not None else bleak.BleakClient(device)

        self._id: int = id
        self._current_track_piece: TrackPiece|None = None
        """Do not use! This can only show the last position for... reasons"""
        self._is_connected = False
        self._road_offset: float|None = None
        self._speed: int = 0
        self._map: Optional[list[TrackPiece]] = None
        self._position: Optional[int] = None

        self.on_track_piece_change: Callable = lambda: None  # Set a dummy function by default
        self._track_piece_future: asyncio.Future = asyncio.Future()
        self._track_piece_watchers: list[_Callback] = []
        self._pong_watchers: list[_Callback] = []
        self._delocal_watchers: list[_Callback] = []
        self._battery_watchers: list[_Callback] = []
        self._controller = controller
        self._battery: BatteryState = battery
        pass

    def _notify_handler(self, handler, data: bytearray):
        """An internal handler function that gets called on a notify receive"""
        msg_type, payload = msg_protocol.disassemble_packet(data)
        if msg_type == const.VehicleMsg.TRACK_PIECE_UPDATE:
            # This gets called when part-way along a track piece (sometimes)
            loc, piece, offset, speed, clockwise = disassemble_track_update(payload)

            # Update internal variables when new info available
            self._road_offset = offset
            self._speed = speed

            # Post a warning when TrackPiece creation failed (but not an error)
            try:
                piece_obj = TrackPiece.from_raw(loc, piece, clockwise)
            except ValueError:
                warn(
                    f"A TrackPiece value received from the vehicle could not be decoded. \
                    If you are running a scan, this will break it. Received: {piece}",
                    errors.TrackPieceDecodeWarning
                )
                return
                pass

            self._current_track_piece = piece_obj
            pass
        elif msg_type == const.VehicleMsg.TRACK_PIECE_CHANGE:
            if (
                self._current_track_piece is not None 
                and self._current_track_piece.type == TrackPieceType.FINISH
            ):
                self._position = 0
            
            uphill_count, downhill_count = disassemble_track_change(payload)[8:10]
            """TODO: Find out what to do with these"""
            # print("Vehicle uphill/downhill:", uphill_count, downhill_count)
            if self._position is not None and self._map is not None:
                # If there was a scan & align already
                self._position += 1
                self._position %= len(self._map)

            self._track_piece_future.set_result(None)
            # Complete internal future when on new track piece.
            # This is used in wait_for_track_change
            self._track_piece_future = asyncio.Future()
            # Create new future since the old one is now done
            self.on_track_piece_change()
            _call_all_soon(self._track_piece_watchers)
            pass
        elif msg_type == const.VehicleMsg.PONG:
            _call_all_soon(self._pong_watchers)
            pass
        elif msg_type == const.VehicleMsg.DELOCALIZED:
            _call_all_soon(self._delocal_watchers)
            pass
        elif msg_type == const.VehicleMsg.CHARGER_INFO:
            self._battery = BatteryState.from_charger_info(payload)
            _call_all_soon(self._battery_watchers)
            pass
        pass

    async def _auto_ping(self):
        # Automatically pings the supercars
        # and disconnects when they don't respond.

        return
        # NOTE:
        # This just returns, because for some reason
        # supercars don't want to respond to pings
        # The code is left here to reimplement should we ever get ping to work
        pong_reply_future = asyncio.Future()
        
        @self.pong
        def pong_watch():
            nonlocal pong_reply_future
            pong_reply_future.set_result()
            pong_reply_future = asyncio.Future()
            print("Pong reply!")
            pass
        
        config = type(self).AUTOMATIC_PING_CONTROL
        timeouts = 0
        while self.is_connected:
            await asyncio.sleep(config["interval"])
            await self.ping()
            print("Ping!")
            try:
                await asyncio.wait_for(pong_reply_future, config["timeout"])
                pass
            except asyncio.TimeoutError:
                timeouts += 1
                print("Ping failed")
                pass
            else:
                timeouts = 0
                print("Ping succeeded")
                pass

            if timeouts > config["max_timeouts"]:
                warn("The vehicle did not sufficiently respond to pings. Disconnecting...")
                await self.disconnect()
            pass
        pass

    async def __send_package(self, payload: bytes):
        """Send a payload to the supercar"""
        if self._write_chara is None:
            raise RuntimeError("A command was sent to a vehicle that has not been connected.")
        try:
            await self._client.write_gatt_char(self._write_chara, payload)
        except OSError as e:
            raise RuntimeError(
                "A command was sent to a vehicle that is already disconnected"
            ) from e
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
        await self._track_piece_future
        # Wait on a new track piece (See _notify_handler)
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
            connect_success = await self._client.connect()
            if not connect_success:
                raise BleakError
            # Handle a failed connect the same way as a BleakError
            pass
        # Translate a bunch of errors occuring on connection
        except BleakDBusError as e:
            raise errors.ConnectionDatabusError(
                "An attempt to connect to the vehicle failed. \
                This can occur sometimes and is usually not an error in your code."
            ) from e
        except BleakError as e:
            raise errors.ConnectionFailedError(
                "An attempt to connect to the vehicle failed. \
                This is usually not associated with your code."
            ) from e
        except asyncio.TimeoutError as e:
            raise errors.ConnectionTimedoutError(
                "An attempt to connect to the vehicle timed out. \
                Make sure the car is actually disconnected."
            ) from e
        
        # Get service and characteristics
        services = self._client.services
        anki_service = services.get_service(const.SERVICE_UUID)
        if anki_service is None:
            raise RuntimeError("The vehicle does not have an anki service... What?")
        read = anki_service.get_characteristic(const.READ_CHAR_UUID)
        write = anki_service.get_characteristic(const.WRITE_CHAR_UUID)
        if read is None or write is None:
            raise RuntimeError(
                "This vehicle does not have a read or write characteristic. \
                If this occurs again, something is severly wrong with your vehicle."
            )

        await self._client.write_gatt_char(
            write,
            set_sdk_pkg(True, 0x1)
        )
        # NOTE: If someone knows what the flags mean, please contact us
        await self._client.start_notify(read, self._notify_handler)

        self._read_chara = read
        self._write_chara = write

        self._is_connected = True
        self._ping_task = asyncio.create_task(self._auto_ping())
        pass

    async def disconnect(self) -> bool:
        """Disconnect from the Supercar

        .. note::
            Remember to execute this for every connected :class:`Vehicle` once the program exits.
            Not doing so will result in your supercars not connecting sometimes
            as they still think they are connected.

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
        except asyncio.TimeoutError as e:
            raise errors.DisconnectTimedoutError(
                "The attempt to disconnect from the vehicle timed out."
            ) from e
        if self._is_connected:
            raise errors.DisconnectFailedError("The attempt to disconnect the vehicle failed.")
        
        if not self._is_connected and self._controller is not None:
            self._controller.vehicles.remove(self)
            self._ping_task.cancel("Vehicle disconnected")
            pass

        return self._is_connected
        pass

    @deprecated_alias(
        "setSpeed",
        doc="""
        Alias to :func:`Vehicle.set_speed`
        
        .. deprecated:: 1.0
            Use alias :func:`Vehicle.set_speed` instead
        """
    )
    async def set_speed(self, speed: int, acceleration: int = 500):
        """Set the speed of the Supercar in mm/s

        :param speed: :class:`int`
            The speed in mm/s
        :param acceleration: :class:`Optional[int]`
            The acceleration in mm/s²
        """
        await self.__send_package(set_speed_pkg(speed, acceleration))
        self._speed = speed
        # Update the internal speed as well
        # (this is technically an overestimate, but the error is marginal)
        pass

    async def stop(self):
        """Stops the Supercar"""
        await self.set_speed(0, 600)
        pass
    
    @deprecated_alias(
        "changeLane",
        doc="""
        Alias to :func:`Vehicle.change_lane`

        .. deprecated:: 1.0
            Use alias :func:`Vehicle.change_lane` instead
        """
    )
    async def change_lane(
            self,
            lane: BaseLane,
            horizontalSpeed: int = 300,
            horizontalAcceleration: int = 300,
            *,
            _hopIntent: int = 0x0,
            _tag: int = 0x0
    ):
        """Change to a desired lane

        :param lane: :class:`BaseLane`
            The lane to move into. These may be :class:`Lane3` or :class:`Lane4`
        :param horizontalSpeed: :class:`Optional[int]`
            The speed the vehicle will move along the track at in mm/s
        :param horizontalAcceleration: :class:`Optional[int]`
            The acceleration in mm/s² the vehicle will move horizontally with
        
        .. note::
            Due to a hardware limitation vehicles won't reliably
            perform lane changes under 300mm/s speed.
        """
        # changeLane is just changePosition but user friendly
        await self.change_position(
            lane.value,
            horizontalSpeed,
            horizontalAcceleration,
            _hopIntent=_hopIntent,
            _tag=_tag
            # NOTE: Getting hop intent and tag to work would be awesome
            # but the vehicles are buggy as ever
        )
        pass
    
    @deprecated_alias(
        "changePosition",
        doc="""
        Alias to :func:`Vehicle.change_position`

        .. deprecated:: 1.0
            Use alias :func:`Vehicle.change_position` instead
        """
    )
    async def change_position(
            self,
            roadCenterOffset: float,
            horizontalSpeed: int = 300,
            horizontalAcceleration: int = 300,
            *,
            _hopIntent: int = 0x0,
            _tag: int = 0x0
    ):
        """Change to a position offset from the track centre
        
        :param roadCenterOffset: :class:`float`
            The target offset from the centre of the track piece in mm
        :param horizontalSpeed: :class:`int`
            The speed the vehicle will move along the track at in mm/s
        :param horizontalAcceleration: :class:`int`
            The acceleration in mm/s² the vehicle will move horizontally with

        .. note::
            Due to a hardware limitation vehicles won't reliably perform
            lane changes under 300mm/s speed.
        """
        await self.__send_package(change_lane_pkg(
            roadCenterOffset,
            horizontalSpeed,
            horizontalAcceleration,
            _hopIntent,
            _tag
        ))
        pass

    async def turn(self, type: int = 3, trigger: int = 0):
        # type and trigger don't work correcty
        """
        .. warning::
            This does not yet function properly. It is advised not to use this method
        """
        if self.map is not None:
            warn(
                "Turning around with a map! This will cause a desync!",
                UserWarning
            )
        await self.__send_package(turn_180_pkg(type, trigger))
        pass
    
    @deprecated_alias(
        "setLights",
        doc="""
        Alias to :func:`Vehicle.set_lights`

        .. deprecated:: 1.0
            Use alias :func:`Vehicle.set_lights` instead
        """
    )
    async def set_lights(self, light: int):
        """Set the lights of the vehicle in accordance with a bitmask

        .. warning::
            This function is deprecated due to not functioning properly.
            It will not execute.
        """
        raise DeprecationWarning(
            "This function is deprecated and does not work due to a bug in the vehicle computer."
        )
        pass
    
    @deprecated_alias(
        "setLightPattern",
        doc="""
        Alias to :func:`Vehicle.set_light_pattern`

        .. deprecated:: 1.0
            Use alias :func:`Vehicle.set_light_pattern` instead
        """
    )
    async def set_light_pattern(self, r: int, g: int, b: int):
        """Set the engine light (the big one) at the top of the vehicle

        .. warning::
            This function is deprecated due to a hardware bug causing it not to function.
            It will not execute.
        """
        raise DeprecationWarning(
            "This function is deprecated and does not work due to a bug in the vehicle computer."
        )
        pass
    
    @deprecated_alias(
        "getLane",
        doc="""
        Alias to :func:`Vehicle.get_lane`

        .. deprecated:: 1.0
            Use alias :func:`Vehicle.get_lane` instead
        """
    )
    def get_lane(self, mode: type[_Lane]) -> Optional[_Lane]:
        """Get the current lane given a specific lane type

        :param mode: :class:`BaseLane`
            A class such as :class:`Lane3` or :class:`Lane4` inheriting from :class:`BaseLane`.
            This is the lane system being used
        
        Returns
        -------
        :class:`Optional[BaseLane]`
            The lane the vehicle is on. This may be none if no lane information is available
            (such as at the start of the program, when the vehicles haven't moved much)
        """
        if self._road_offset is None:
            return None
        else:
            return mode.get_closest_lane(self._road_offset)
        pass

    async def align(
            self,
            speed: int=300,
            *,
            target_previous_track_piece_type: TrackPieceType = TrackPieceType.FINISH
    ):
        """Align to the start piece.

        :param speed: :class:`int`
            The speed the vehicle should travel at during alignment
        """
        await self.set_speed(speed)
        while self._current_track_piece is None\
                or self._current_track_piece.type is not target_previous_track_piece_type:
            # Waits until the previous track piece was FINISH (by default).
            # This means the current position is START
            await self.wait_for_track_change()
            pass

        self._position = 0
        # Vehicle is now at START which is always 0

        await self.stop()
        pass
    
    @deprecated_alias(
        "trackPieceChange",
        doc="""
        Alias to :func:`Vehicle.track_piece_change`

        .. deprecated:: 1.0
            Use :func:`Vehicle.track_piece_change` instead
        """
    )
    def track_piece_change(self, func: _Callback):
        """
        A decorator marking a function to be executed when the supercar
        drives onto a new track piece

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
    
    @deprecated_alias(
        "removeTrackPieceWatcher",
        doc="""
        Alias to :func:`Vehicle.remove_track_piece_change`

        .. deprecated:: 1.0
            Use :func:`Vehicle.remove_track_piece_watcher` instead
        """
    )
    def remove_track_piece_watcher(self, func: _Callback):
        """
        Remove a track piece event handler added by :func:`Vehicle.track_piece_change`

        :param func: :class:`function`
            The function to remove as an event handler
        
        Raises
        ------
        :class:`ValueError`
            The function passed is not an event handler
        """
        self._track_piece_watchers.remove(func)
        pass

    def delocalized(self, func: _Callback):
        """
        A decorator marking this function to be execute when the vehicle has delocalized*.

        :param func: :class:`function`
            The listening function

        .. note::
            It is not guaranteed that the handler will be called when the vehicle is delocalized.
            Furthermore, it is not guaranteed that the handler will *not* be called when the
            vehicle is still localized.
            This method should only be used for informational purposes!
        """
        self._delocal_watchers.append(func)
        pass

    def remove_delocalized_watcher(self, func: _Callback):
        """
        Remove a delocalization event handler that was added by :func:`Vehicle.delocalized`.

        :param func: :class:`function`
            The function to be removed

        Raises
        ------
        :class:`ValueError`
            The function passed is not an event handler
        """
        self._delocal_watchers.remove(func)
        pass

    def battery_change(self, func: _Callback):
        """
        Register a callback to execute on changes to the battery state.
        
        .. note::
            It is not guaranteed that the battery state has actually changed
            from the last callback.
            Further note that this function is not called on startup.
        
        Raises
        ------
        :class:`ValueError`
            The function passed is not an event handler
        """
        self._battery_watchers.append(func)
        pass

    def remove_battery_watcher(self, func: _Callback):
        self._battery_watchers.remove(func)
        pass

    async def ping(self):
        """
        .. warning::
            Due to a bug in the firmware, supercars will never respond to pings!
        
        Send a ping to the vehicle
        """
        await self.__send_package(msg_protocol.const.ControllerMsg.PING)
        pass

    def pong(self, func):
        """
        .. warning::
            Due to a bug in the firmware, supercars will never respond to pings!
        
        A decorator marking an function to be executed when the supercar responds to a ping

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
    def current_track_piece(self) -> TrackPiece|None:
        """
        The :class:`TrackPiece` the vehicle is currently located at

        .. note::
            This will return :class:`None` if either scan or align is not completed
        """
        if self.map is None or self.map_position is None:
            # If scan or align not complete, we can't find the track piece
            return None
            pass
        return self.map[self.map_position]
        pass

    @property
    def map(self) -> tuple[TrackPiece, ...]|None:
        """
        The map the :class:`Vehicle` instance is using.
        This is :class:`None` if the :class:`Vehicle` does not have a map supplied.
        """
        return tuple(self._map) if self._map is not None else None
        pass

    @property
    def map_position(self) -> int|None:
        """
        The position of the :class:`Vehicle` instance on the map.
        This is :class:`None` if :func:`Vehicle.align` has not yet been called.
        """
        return self._position
        pass

    @property
    def road_offset(self) -> float|None:
        """
        The offset from the road centre.
        This is :class:`None` if the supercar did not send any information yet.
        (Such as when it hasn't moved much)
        """
        return self._road_offset
        pass

    @property
    def speed(self) -> int:
        """
        The speed of the supercar in mm/s.
        This is :class:`None` if the supercar has not moved or :func:`Vehicle.setSpeed`
        hasn't been called yet.
        """
        return self._speed
        pass

    @property
    def current_lane3(self) -> Optional[Lane3]:
        """
        Short-hand for
        
        .. code-block:: python
            
            Vehicle.get_lane(Lane3)
        """
        return self.get_lane(Lane3)
        pass

    @property
    def current_lane4(self) -> Optional[Lane4]:
        """
        Short-hand for
        
        .. code-block:: python
            
            Vehicle.get_lane(Lane4)
        """
        return self.get_lane(Lane4)
        pass

    @property
    def id(self) -> int:
        """
        The id of the :class:`Vehicle` instance. This is set during initialisation of the object.
        """
        return self._id
        pass

    @property
    def battery_state(self) -> BatteryState:
        """
        The state of the supercar's battery
        """
        return self._battery
        pass
    pass
