import anki

class Car:
    def __init__(self, id: int, controller: anki.Controller):
        self._controller = controller
        self._id = id

    async def create_vehicle(self):
        self._vehicle = await self._controller.connectOne(vehicle_id=self._id)
        self._id = self._vehicle.id
    
    async def delete(self):
        await self._vehicle.disconnect()

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