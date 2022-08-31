import anki

class Car:
    def __init__(self, id: int, controller: anki.Controller):
        self._controller = controller
        self._id = id

    async def create_vehicle(self):
        """Connects to the Supercar"""
        self._vehicle = await self._controller.connectOne(vehicle_id=self._id)
        self._id = self._vehicle.id
    
    async def delete(self):
        """Disconnectes from the Supercar"""
        await self._vehicle.disconnect()

    async def set_speed(self, speed: int, acceleration: int = 500):
        """Set the speed of the Supercar in mm/s

        :param speed: :class:`int`An integer value describing the target speed in mm/s
        :param acceleration: :class:`int` An integer value denoting the acceleration used to move to the target speed
        """
        await self._vehicle.setSpeed(speed, acceleration)
    
    async def scan(self):
        return await self._controller.scan()

    @property
    def id(self):
        return self._id
    
    @property
    def speed(self):
        return self._vehicle.speed

    @property
    def current_track_piece(self):
        return self._vehicle.current_track_piece

    @property
    def map(self):
        return self._vehicle.map

    @property
    def is_connected(self):
        return self._vehicle.is_connected