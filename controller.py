import bleak, asyncio
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from .const import *
from . import errors
from .vehicle import Vehicle, interpretLocalName
from .track_pieces import TrackPiece
from .scanner import Scanner

from typing import Optional

def isAnki(device : BLEDevice, advertisement : AdvertisementData):
    try:
        state, version, name = interpretLocalName(advertisement.local_name)
    except ValueError:
        return False
        pass
    if state.charging: return False

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
    __slots__ = ["_scanner","timeout","vehicles","map"]
    def __init__(self,*,timeout : float = 10):
        self._scanner = bleak.BleakScanner()
        self.timeout = timeout
        self.vehicles : set[Vehicle] = set()
        self.map : Optional[list[TrackPiece]] = None
        pass

    async def _get_vehicle(self, address : str = None) -> Vehicle:
        """Finds a Supercar and creates a Vehicle instance around it"""
        device = await self._scanner.find_device_by_filter(lambda device, advertisement: isAnki(device,advertisement) and (address is None or device.address == address))
        if device is None:
            raise errors.VehicleNotFound("Could not find a supercar within the given timeout")
            pass

        client = bleak.BleakClient(device)

        vehicle = Vehicle(device,client)
        self.vehicles.add(vehicle)
        return vehicle
        pass


    async def connect_one(self) -> Vehicle:
        """Connect to one non-charging Supercar and return the Vehicle instance"""
        vehicle = await self._get_vehicle()
        await vehicle.connect()
        return vehicle
        pass

    async def connect_specific(self, address : str) -> Vehicle:
        """Connect to a supercar with a specified MAC address"""
        vehicle = await self._get_vehicle(address)
        await vehicle.connect()
        return vehicle
        pass

    async def connect_many(self, amount : int) -> set[Vehicle]:
        """Connect to <amount> non-charging Supercars"""
        return {await self.connect_one() for i in range(amount)} # Done in series because the documentation said that would be more stable
        pass

    
    async def scan(self) -> list[TrackPiece]:
        if self.map is not None:
            raise errors.DuplicateScanWarning("The map has already been scanned. Check your code for any mistakes like that.")
            pass

        vehicle = self.vehicles.pop()
        self.vehicles.add(vehicle)

        scanner = Scanner(vehicle)
        self.map = await scanner.scan()

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

        for lvehicle in self.vehicles: 
            asyncio.create_task(align(lvehicle))
            await lvehicle.setSpeed(300)
            completed_tasks[lvehicle] = False
            pass

        while not all(completed_tasks.values()): await asyncio.sleep(0) # Wait until all tasks are done

        for lvehicle in self.vehicles:
            lvehicle._map = self.map
            lvehicle._position = self.map_types.index(TrackPieceTypes.START) # Assumes every vehicle is on the same track piece at the start
            pass

        # print([vehicle._position for vehicle in self.vehicles])

        for v in self.vehicles: v._position = 0

        return self.map
        pass



    async def disconnect_all(self):
        await asyncio.gather(*[vehicle.disconnect() for vehicle in self.vehicles])
        pass
    
    def handle_shutdown(self):
        """Handles a shutdown neatly and disconnects the vehicles"""
        asyncio.run(self.disconnect_all())
        pass


    @property
    def map_types(self) -> tuple:
        return tuple([track_piece.type for track_piece in self.map])
        pass
    pass