import bleak, asyncio
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from ..utility.const import *
from .. import errors
from ..vehicle import Vehicle, interpretLocalName
from ..utility.track_pieces import TrackPiece
from .scanner import Scanner

from typing import Iterable, Optional

def isAnki(device : BLEDevice, advertisement : AdvertisementData):
    try:
        state, version, name = interpretLocalName(advertisement.local_name)
    except ValueError: # Catch error if name is not interpretable (not a vehicle then)
        return False
        pass
    if state.charging: return False # We don't want to connect to a charging vehicle, so we'll just pretend it's not a vehicle

    return True
    # Service check doesn't work as the Supercars don't seem to advertise their services o.0
    ankiFound = False
    for service_uuid in advertisement.service_uuids:
        ankiFound = (service_uuid.lower() == SERVICE_UUID)
        if ankiFound: break
        pass
    return ankiFound
    pass

class Controller:
    """This object controls all vehicle connections. With it you can connect to any number of vehicles and disconnect cleanly.
    ## Paramaters\n
    timeout=10: The time until the controller gives up searching for a vehicle."""
    __slots__ = ["_scanner","timeout","vehicles","map"]
    def __init__(self,*,timeout : float = 10):
        self._scanner = bleak.BleakScanner()
        self.timeout = timeout
        self.vehicles : set[Vehicle] = set()
        self.map : Optional[list[TrackPiece]] = None
        pass

    async def _getVehicle(self,vehicle_id : Optional[int] = None, address : str = None) -> Vehicle:
        """Finds a Supercar and creates a Vehicle instance around it"""

        device = await self._scanner.find_device_by_filter(lambda device, advertisement: isAnki(device,advertisement) and (address is None or device.address == address))
        if device is None:
            raise errors.VehicleNotFound("Could not find a supercar within the given timeout")
            pass

        client = bleak.BleakClient(device)

        if vehicle_id is None:
            vehicle_id = id(client)
            pass

        vehicle = Vehicle(vehicle_id, device,client)
        self.vehicles.add(vehicle)
        return vehicle
        pass


    async def connectOne(self, vehicle_id : Optional[int] = None) -> Vehicle:
        """Connect to one non-charging Supercar and return the Vehicle instance

        ## Parameters\n
        + Optional `vehicle_id`: The id given to the `Vehicle` instance on connection

        ## Returns\n
        A `Vehicle` object representing the connected supercar

        ## Raises\n
        + `VehicleNotFound`: No supercar was found in the set timeout\n
        + `ConnectionTimedoutException`: The connection attempt to the supercar did not succeed within the set timeout
        + `ConnectionDatabusException`: A databus error occured whilst connecting to the supercar\n
        + `ConnectionFailedException`: A generic error occured whilst connection to the supercar"""
        vehicle = await self._getVehicle(vehicle_id)
        await vehicle.connect()
        return vehicle
        pass

    async def connectSpecific(self, address : str, vehicle_id : Optional[int] = None) -> Vehicle:
        """Connect to a supercar with a specified MAC address
        
        ## Parameters\n
        + `address`: A string representing the MAC-address of the vehicle to connect to. This needs to be uppercase seperated by colons\n
        + Optional `vehicle_id`: An integer id given to the vehicle on connection.\n

        ## Returns\n
        A `Vehicle` object representing the connected supercar
        
        ## Raises\n
        + `VehicleNotFound`: No supercar was found in the set timeout\n
        + `ConnectionTimedoutException`: The connection attempt to the supercar did not succeed within the set timeout
        + `ConnectionDatabusException`: A databus error occured whilst connecting to the supercar\n
        + `ConnectionFailedException`: A generic error occured whilst connection to the supercar"""
        vehicle = await self._getVehicle(vehicle_id,address)
        await vehicle.connect()
        return vehicle
        pass

    async def connectMany(self, amount : int, vehicle_ids : Iterable[int] = None) -> tuple[Vehicle]:
        """Connect to <amount> non-charging Supercars
        
        ## Parameters\n
        + `amount`: An integer amount representing the number of vehicles to connect to\n
        + Optional `vehicled_ids`: An iterable with the ids the vehicles will get on connection. These entries may be None.\n

        ## Returns\n
        A tuple of connected `Vehicle` instances.

        ## Raises\n
        + `ValueError`: The amount of requested supercars does not match the length of `vehicle_ids`.\n
        + `VehicleNotFound`: No supercar was found in the set timeout\n
        + `ConnectionTimedoutException`: The connection attempt to the supercar did not succeed within the set timeout
        + `ConnectionDatabusException`: A databus error occured whilst connecting to the supercar\n
        + `ConnectionFailedException`: A generic error occured whilst connection to the supercar
        """

        if vehicle_ids is None: vehicle_ids = [None]*amount
        if amount != len(vehicle_ids): raise ValueError("Amount of passed vehicle ids is different to amount of requested connections")

        return tuple([await self.connectOne(vehicle_id) for vehicle_id in vehicle_ids]) # Done in series because the documentation said that would be more stable
        pass

    
    async def scan(self, align_pre_scan : bool = True) -> list[TrackPiece]:
        if self.map is not None:
            raise errors.DuplicateScanWarning("The map has already been scanned. Check your code for any mistakes like that.")
            pass

        async def noScanAlign(vehicle : Vehicle, align_target = TrackPieceTypes.FINISH):
            await vehicle.setSpeed(250)
            while vehicle._current_track_piece is None or vehicle._current_track_piece.type != align_target:
                await asyncio.sleep(0.1)
                pass

            await vehicle.stop()
            pass

        if align_pre_scan:
            await asyncio.gather(*[noScanAlign(v,TrackPieceTypes.FINISH) for v in self.vehicles])
            await asyncio.sleep(1)
            pass

        temp_vehicles = self.vehicles.copy()
        scan_vehicle = temp_vehicles.pop()

        async def simulAlign(vehicle : Vehicle):
            await asyncio.sleep(1)
            await noScanAlign(vehicle)
            pass

        scanner = Scanner(scan_vehicle)
        
        await scan_vehicle.setSpeed(150)
        await asyncio.sleep(1)
        await scan_vehicle.stop()

        if not align_pre_scan:
            tasks = [asyncio.create_task(simulAlign(v)) for v in temp_vehicles]
            pass
        self.map = await scanner.scan()

        if not align_pre_scan: 
            for task in tasks: await task

        completed_tasks  = {}
        async def align(vehicle : Vehicle):
            while True:
                await vehicle.wait_for_track_change()
                track=vehicle._current_track_piece
                if track is not None and track.type is TrackPieceTypes.FINISH:
                    break
                    pass
                pass

            await vehicle.stop()

            completed_tasks[vehicle] = True
            pass

        # for v in self.vehicles: 
        #     asyncio.create_task(align(v))
        #     await v.setSpeed(300)
        #     completed_tasks[v] = False
        #     pass

        # while not all(completed_tasks.values()): await asyncio.sleep(0) # Wait until all tasks are done

        for v in self.vehicles:
            v._map = self.map
            v._position = -1 if v in temp_vehicles else 0 # Scanner is always one piece ahead
            pass

        return self.map
        pass



    async def disconnectAll(self):
        await asyncio.gather(*[vehicle.disconnect() for vehicle in self.vehicles])
        pass
    
    def handleShutdown(self):
        """Handles a shutdown neatly and disconnects the vehicles"""
        asyncio.run(self.disconnectAll())
        pass


    @property
    def map_types(self) -> tuple:
        return tuple([track_piece.type for track_piece in self.map])
        pass
    pass