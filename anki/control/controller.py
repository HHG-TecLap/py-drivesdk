import bleak
import asyncio
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from ..misc.const import TrackPieceType
from .. import errors
from .vehicle import Vehicle, interpret_local_name
from ..misc.track_pieces import TrackPiece
from .scanner import BaseScanner, Scanner

from typing import Optional
from collections.abc import Collection


def _is_anki(device: BLEDevice, advertisement: AdvertisementData):
    try:
        state, version, name = interpret_local_name(advertisement.local_name)
    except ValueError:
        # If we can't interprete the name, it can't be a vehicle
        return False
        pass
    if state.on_charger:
        # We don't want to connect to a charging vehicle, 
        # so we'll just pretend it's not a vehicle
        return False

    return True


class Controller:
    """
    This object controls all vehicle connections.
    With it you can connect to any number of vehicles and disconnect cleanly.

    :param timeout: :class:`float` The time until the controller gives up searching for a vehicle.
    """
    __slots__ = (
        "_scanner",
        "timeout",
        "vehicles",
        "map",
    )

    def __init__(self, *, timeout: float=10):
        self._scanner = bleak.BleakScanner()
        self.timeout = timeout
        self.vehicles: set[Vehicle] = set()
        self.map: Optional[list[TrackPiece]] = None
        pass

    async def _get_vehicle(
            self,
            vehicle_id: Optional[int]=None,
            address: str|None=None
    ) -> Vehicle:
        # Finds a Supercar and creates a Vehicle instance around it
        device = await self._scanner.find_device_by_filter(
            lambda device, advertisement:
                _is_anki(device, advertisement)
                and (address is None or device.address == address),
            timeout=self.timeout
        )  # type: ignore
        # Get a BLEDevice and ensure it is of a required address if address was given
        if device is None:
            raise errors.VehicleNotFoundError("Could not find a supercar within the given timeout")
            pass

        client = bleak.BleakClient(device)

        vehicle_ids = {v.id for v in self.vehicles}
        if vehicle_id is None:
            # Automatically assign generate unused vehicle id
            vehicle_id = 1024
            while vehicle_id in vehicle_ids:
                vehicle_id += 1
                pass
            pass
        elif vehicle_id in vehicle_ids:
            raise RuntimeError(f"Duplicate id for vehicle. Id {vehicle_id} already in use.")

        vehicle = Vehicle(
            vehicle_id,
            device,
            client,
            self,
            battery=interpret_local_name(device.name)[0]
        )
        self.vehicles.add(vehicle)
        return vehicle
        pass

    async def connect_one(
            self,
            vehicle_id: Optional[int]=None
    ) -> Vehicle:
        """Connect to one non-charging Supercar and return the Vehicle instance

        :param vehicle_id: :class:`Optional[int]`
            The id given to the :class:`Vehicle` instance on connection


        Returns
        -------
        :class:`Vehicle`
            The connected supercar


        Raises
        ------
        :class:`VehicleNotFound`
            No supercar was found in the set timeout
        
        :class:`ConnectionTimedoutException`
            The connection attempt to the supercar did not succeed within the set timeout
        
        :class:`ConnectionDatabusException`
            A databus error occured whilst connecting to the supercar
        
        :class:`ConnectionFailedException`
            A generic error occured whilst connection to the supercar

        :class:`RuntimeError`
            A vehicle with the specified id already exists.
            This will only be raised when using a custom id.
        """
        vehicle = await self._get_vehicle(vehicle_id)
        vehicle._map = self.map
        # If there is no map it sets None which is the default for Vehicle._map anyway
        await vehicle.connect()
        return vehicle
        pass

    async def connect_specific(
            self,
            address: str,
            vehicle_id: Optional[int]=None
    ) -> Vehicle:
        """Connect to a supercar with a specified MAC address
        
        :param address: :class:`str`
            The MAC-address of the vehicle to connect to. Needs to be uppercase seperated by colons
        :param vehicle_id: :class:`int`
            The id passed to the :class:`Vehicle` object on its creation

        Returns
        -------
        :class:`Vehicle`
            The connected supercar
        
        Raises
        ------
        :class:`VehicleNotFound`
            No supercar was found in the set timeout
        
        :class:`ConnectionTimedoutException`
            The connection attempt to the supercar did not succeed within the set timeout
        
        :class:`ConnectionDatabusException`
            A databus error occured whilst connecting to the supercar
        
        :class:`ConnectionFailedException`
            A generic error occured whilst connection to the supercar

        :class:`RuntimeError`
            A vehicle with the specified id already exists.
            This will only be raised when using a custom id.
        """
        vehicle = await self._get_vehicle(vehicle_id, address)
        await vehicle.connect()
        return vehicle
        pass
    
    async def connect_many(
            self,
            amount: int,
            vehicle_ids: Collection[int|None]|None=None
    ) -> tuple[Vehicle, ...]:
        """Connect to <amount> non-charging Supercars
        
        :param amount: :class:`int`
            The amount of vehicles to connect to
        :param vehicle_ids: :class:`Optional[Iterable[int]]`
            The vehicle ids passed to the :class:`Vehicle` instances

        Returns
        -------
        :class:`tuple[Vehicle]`
            The connected supercars

        Raises
        ------
        :class:`ValueError`
            The amount of requested supercars does not match the length of :param vehicle_ids:

        :class:`VehicleNotFound`
            No supercar was found in the set timeout

        :class:`ConnectionTimedoutException`
            A connection attempt to one of the supercars timed out

        :class:`ConnectionDatabusException`
            A databus error occured whilst connecting to a supercar

        :class:`ConnectionFailedException`
            A generic error occured whilst connecting to a supercar
        
        :class:`RuntimeError`
            A vehicle with the specified id already exists.
            This will only be raised when using a custom id.
        """

        if vehicle_ids is None:
            vehicle_ids = [None] * amount
        if amount != len(vehicle_ids):
            raise ValueError(
                "Amount of passed vehicle ids is different to amount of requested connections"
            )

        return tuple([
            await self.connect_one(vehicle_id)
            for vehicle_id in vehicle_ids]
        )
        # Done in series because the documentation said that would be more stable
        pass

    async def scan(
            self,
            scan_vehicle: Vehicle|None=None,
            /,
            align_pre_scan: bool=True,
            scanner_class: type[BaseScanner]=Scanner
    ) -> list[TrackPiece]:
        """Assembles a digital copy of the map and adds it to every connected vehicle.
        
        :param scan_vehicle: :class:`Optional[Vehicle]`
            When passed a Vehicle object, this Vehicle will be used as a scanner. Otherwise one
            will be selected automatically.
        :param align_pre_scan: :class:`bool`
            When set to True, the supercars can start from any position on the map and align
            automatically before scanning. Disabling this means your supercars need to start
            between START and FINISH
        :param scanner_class: :class:`type`
            The type of scanner used

        Returns
        -------
        :class:`list[TrackPiece]`
            The resulting map

        Raises
        ------
        :class:`DuplicateScanWarning`
            The map was already scanned in. This scan will be skipped.
        """
        if self.map is not None:
            # The map shouldn't be scanned twice.
            # Exiting the method is a good practice implementation
            raise errors.DuplicateScanWarning(
                "The map has already been scanned. Check your code for any mistakes like that."
            )

        vehicles_no_scan = self.vehicles.copy()
        if scan_vehicle is None:
            scan_vehicle = vehicles_no_scan.pop()
            # This allows us to use temp_vehicles as a set of all non-scannning vehicles
        else:
            vehicles_no_scan.remove(scan_vehicle)
            # Remove the scanning vehicle from the set if it is already passed as an argument
        
        scanner = scanner_class(scan_vehicle)

        if align_pre_scan:
            # Aligning before scanning if enabled.
            # This allows the vehicles to be placed anywhere on the map
            await asyncio.gather(*[scanner.align(v) for v in self.vehicles])
            # Since we're aligning BEFORE scan, we need the piece before
            # the one we want to align in front of
            await asyncio.sleep(1)
            pass

        async def simul_align(vehicle: Vehicle):
            await asyncio.sleep(1)
            # Putting a little delay here so that the other vehicles
            # aren't in front of the scanner which would ruin the alignment
            await scanner.align(vehicle)
            pass
        
        await scan_vehicle.set_speed(150)
        # Drive a little forward so that we don't immediately
        # see START and FINISH and complete the scan
        await asyncio.sleep(1)
        await scan_vehicle.stop()

        tasks = []
        if not align_pre_scan:
            # Only aligning during scan when not already aligned pre-scan.
            # Without pre-align this is neccessary to ensure that
            # the vehicles are where we think they are
            tasks = [asyncio.create_task(simul_align(v)) for v in vehicles_no_scan]
            pass
        self.map = await scanner.scan()

        for task in tasks:
            await task

        for v in self.vehicles:
            v._map = self.map
            v._position = len(self.map) - 1 if v in vehicles_no_scan else 0
            # Scanner is always one piece ahead
            pass

        return self.map
        pass

    async def disconnect_all(self):
        """Disconnects from all the connected supercars
        
        Raises
        ------
        :class:`DisconnectTimedoutException`
            A disconnection attempt timed out
        :class:`DisconnectFailedException`
            A disconnection attempt failed for unspecific reasons
        """
        # Disconnect done in parallel as opposed to connect as the clients are already established
        await asyncio.gather(*[vehicle.disconnect() for vehicle in self.vehicles])
        pass

    async def __aenter__(self):
        return self
        pass

    async def __aexit__(self, *args):
        await self.disconnect_all()
        pass

    @property
    def map_types(self) -> tuple[TrackPieceType, ...]|None:
        if self.map is None:
            return None
        # Converting to a tuple to prevent DAUs (that's German) thinking they can affect the map
        return tuple(track_piece.type for track_piece in self.map)
    pass
