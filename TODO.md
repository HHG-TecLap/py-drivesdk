# Todo-List

+ Catch `asyncio.TimeoutError` in `Vehicle.disconnect` on `self.__client__.disconnect`

+ Fix map_position breaking when turning around
    (i.e. add smart position detection)

+ Try and decode new message types
    + battery level (C2V & V2C)
    + road center offset update (V2C)
    + delocalization (V2C)
    + ping (C2V &V2C)
    + try and rediscover setLights and setEngineLights based on another library

+ Write a Documentation
