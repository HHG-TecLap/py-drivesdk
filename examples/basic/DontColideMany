import anki, asyncio
from aioconsole import ainput

Locks: list[asyncio.Lock] = []
Tasks: list[asyncio.Task] = []

async def OnTrackChange(vehicle:anki.Vehicle, speed: int):
    while True:
        if Locks[vehicle.map_position].locked():
            await vehicle.stop()
        async with Locks[vehicle.map_position]:
            if Locks[(vehicle.map_position+1)%len(Locks)].locked():
                await vehicle.stop()
                while Locks[(vehicle.map_position+1)%len(Locks)].locked():
                    await asyncio.sleep(0.01)
            await vehicle.setSpeed(speed)
            await vehicle.wait_for_track_change()

async def main():
    controller = anki.Controller()
    crossings =[(4,12),(6,20),(9,19)]
    vehicles:list(anki.Vehicle) = []
    
    vehicles.append(await controller.connectOne())
    await controller.scan()
    for i in range(5):
        print("start shifting")
        for j in range(len(vehicles)):
            await vehicles[j].setSpeed(300)
            while(vehicles[j].map_position != i-j+1):
                await asyncio.sleep(0.001)
            await vehicles[j].stop()
        while True:
            await ainput("Continue")
            try:
                vehicles.append(await controller.connectOne())
            except Exception as e:
                print(e)
            else:
                break
        await vehicles[i+1].align()
        print("vehicle aligned")
    
    
    for piece in controller.map:
        Locks.append(asyncio.Lock())
    for cross in crossings:
        Locks[cross[1]] = Locks[cross[0]]


    for i,v in enumerate(vehicles): 
        Tasks.append(asyncio.create_task(OnTrackChange(v,i*50+300)))
        await v.setSpeed(300) 
    await asyncio.sleep(1000)
    try:
        while True:
            await asyncio.sleep(10000)
            pass
    finally:
        await controller.disconnectAll()
        pass
    pass

# Only running the main function when actually executing this program
if __name__ == "__main__": asyncio.run(main())