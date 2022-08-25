import bleak, asyncio
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from ..utility.const import *
from .. import errors
from .vehicle import Vehicle, interpretLocalName
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
    :param timeout: The time until the controller gives up searching for a vehicle. (defaults to 10)
    :type timeout: float
    """
    __slots__ = ["_scanner","timeout","vehicles","map"]
    def __init__(self,*,timeout : float = 10):
        self._scanner = bleak.BleakScanner()
        self.timeout = timeout
        self.vehicles : set[Vehicle] = set()
        self.map : Optional[list[TrackPiece]] = None
        pass

    async def _getVehicle(self,vehicle_id : Optional[int] = None, address : str = None) -> Vehicle:
        """Finds a Supercar and creates a Vehicle instance around it"""

        device = await self._scanner.find_device_by_filter(lambda device, advertisement: isAnki(device,advertisement) and (address is None or device.address == address), timeout=self.timeout)
        # Get a BLEDevice and ensure it is of a required address if address was given
        if device is None:
            raise errors.VehicleNotFound("Could not find a supercar within the given timeout")
            pass

        client = bleak.BleakClient(device) # Wrapping the device in a client. This client will be used to send and receive data in the Vehicle class

        if vehicle_id is None: # Assign the object id of the client as a vehicle id if it wasn't given. This ensures that every vehicle has an id
            vehicle_id = id(client)
            pass

        vehicle = Vehicle(vehicle_id, device,client, self)
        self.vehicles.add(vehicle)
        return vehicle
        pass


    async def connectOne(self, vehicle_id : Optional[int] = None) -> Vehicle:
        """Connect to one non-charging Supercar and return the Vehicle instance

        :param vehicle_id: The id given to the `Vehicle` instance on connection (Optional)
        :type vehicle_id: int

        :return: A `Vehicle` object representing the connected supercar
        :rtype: anki.Vehicle

        :raise anki.errors.VehicleNotFound: No supercar was found in the set timeout
        :raise anki.errors.ConnectionTimedoutException: The connection attempt to the supercar did not succeed within the set timeout
        :raise anki.errors.ConnectionDatabusException: A databus error occured whilst connecting to the supercar
        :raise anki.errors.ConnectionFailedException: A generic error occured whilst connection to the supercar
        """
        vehicle = await self._getVehicle(vehicle_id)
        vehicle._map = self.map # Add an existing map to the vehicle. If there is no map it sets None which is the default for Vehicle._map anyway
        await vehicle.connect()
        return vehicle
        pass

    async def connectSpecific(self, address : str, vehicle_id : Optional[int] = None) -> Vehicle:
        """Connect to a supercar with a specified MAC address
        
        ## Parameters\n
        + `address`: A string representing the MAC-address of the vehicle to connect to. This needs to be uppercase seperated by colons\n
        + Optional `vehicle_id`: An integer id given to the vehicle on connection.\n

        :return: A `Vehicle` object representing the connected supercar
        :rtype: anki.Vehicle

        :raise anki.errors.VehicleNotFound: No supercar was found in the set timeout
        :raise anki.errors.ConnectionTimedoutException: The connection attempt to the supercar did not succeed within the set timeout
        :raise anki.errors.ConnectionDatabusException: A databus error occured whilst connecting to the supercar
        :raise anki.errors.ConnectionFailedException: A generic error occured whilst connection to the supercar
        """
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

    
    async def scan(self, scan_vehicle : Vehicle = None, align_pre_scan : bool = True) -> list[TrackPiece]:
        """Assembles a digital copy of the map and adds it to every connected vehicle.
        
        ## Parameters\n
        + Optional `scan_vehicle`: When passed a Vehicle object, this Vehicle will be used as a scanner. Otherwise it will be selected automatically.
        + Optional `align_pre_scan`: When set to True, the supercars can start from any position on the map and align automatically before scanning. Disabling this means your supercars need to start between START and FINISH

        ## Returns\n
        A list of track pieces representing the scanned in map.

        ## Raises\n
        + `DuplicateScanWarning`: The map was already scanned in. This scan will be skipped.
        """
        if self.map is not None: # The map shouldn't be scanned twice. Exiting the method is a good practice implementation
            raise errors.DuplicateScanWarning("The map has already been scanned. Check your code for any mistakes like that.")
            pass

        async def noScanAlign(vehicle : Vehicle, align_target = TrackPieceTypes.FINISH): # Alignment when the scanner is not currently running
            await vehicle.setSpeed(250)
            while vehicle._current_track_piece is None or vehicle._current_track_piece.type != align_target: # Don't check when none to prevent AttributeError
                await asyncio.sleep(0.1)
                pass

            await vehicle.stop()
            pass

        temp_vehicles = self.vehicles.copy()
        if scan_vehicle is None:
            scan_vehicle = temp_vehicles.pop() # Take a vehicle out of the set. This allows us to use temp_vehicles as a set of all non-scannning vehicles
        else:
            temp_vehicles.remove(scan_vehicle) # Remove the scanning vehicle from the set if it is already passed as an argument

        if align_pre_scan: # Aligning before scanning if enabled. This allows the vehicles to be placed anywhere on the map
            await asyncio.gather(*[noScanAlign(v,TrackPieceTypes.FINISH) for v in self.vehicles]) # Since we're aligning BEFORE scan, we need the piece before the one we want to align in front of
            await asyncio.sleep(1)
            pass

        async def simulAlign(vehicle : Vehicle):
            await asyncio.sleep(1) # Putting a little delay here so that the other vehicles aren't in front of the scanner which would ruin the alignment
            await noScanAlign(vehicle)
            pass

        scanner = Scanner(scan_vehicle)
        
        await scan_vehicle.setSpeed(150) # Drive a little forward so that we don't immediately see START and FINISH and complete the scan
        await asyncio.sleep(1)
        await scan_vehicle.stop()

        if not align_pre_scan: # Only aligning during scan when not already aligned pre-scan. Without pre-align this is neccessary to ensure that the vehicles are where we think they are
            tasks = [asyncio.create_task(simulAlign(v)) for v in temp_vehicles]
            pass
        self.map = await scanner.scan()

        if not align_pre_scan: # Wait until all alignments are completed
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
        """Disconnects from all the connected supercars
        
        ## Raises\n
        + `DisconnectTimedoutException`: A disconnection attempt timed out\n
        + `DisconnectFailedException`: A disconnection attempt failed for unspecific reasons
        """
        await asyncio.gather(*[vehicle.disconnect() for vehicle in self.vehicles]) # Disconnect done in parallel as opposed to connect as the clients are already established
        pass

    async def __aenter__(self):
        return self
        pass

    async def __aexit__(self,*args):
        await self.disconnectAll()
        pass
    
    def handleShutdown(self):
        """Handles a shutdown neatly and disconnects the vehicles
        
        ## Raises\n
        + `DisconnectTimedoutException`: A disconnection attempt timed out\n
        + `DisconnectFailedException`: A disconnection attempt failed for unspecific reasons"""
        asyncio.run(self.disconnectAll())
        pass


    @property
    def map_types(self) -> tuple:
        return tuple([track_piece.type for track_piece in self.map]) # Converting to a tuple to prevent DAUs thinking they can affect the map
        pass
    pass
