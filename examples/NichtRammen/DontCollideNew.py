import anki, asyncio
crossings =[(4,12),(6,20),(9,19)]
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
    async with anki.Controller() as control:
        vehicles = await control.connectMany(2) 
        await control.scan()

        
        for piece in control.map:
            Locks.append(asyncio.Lock())
        for cross in crossings:
            Locks[cross[1]] = Locks[cross[0]]


        for i,v in enumerate(vehicles): 
            Tasks.append(asyncio.create_task(OnTrackChange(v,i*100+300)))
            await v.setSpeed(300) 
        await asyncio.sleep(1000)
        
        for v in vehicles:
            await v.stop()


if __name__ == "__main__": asyncio.run(main())
