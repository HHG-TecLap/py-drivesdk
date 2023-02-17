import anki, asyncio
from aioconsole import ainput

async def main():
    controller = anki.Controller()

    vehicles:list(anki.Vehicle) = []
    
    vehicle = await controller.connectOne()
    vehicles.append(vehicle)
    await controller.scan()
    for i in range(4):
        print("start shifting")
        for j in range(len(vehicles)):
            curPos = vehicles[j].map_position
            await vehicles[j].setSpeed(300)
            while(vehicles[j].map_position != curPos +1):
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
    
    try:
        while True:
            await vehicle.wait_for_track_change()
            print(
                "The vehicle is currently at",vehicle.current_track_piece.type,
                "that is the", vehicle.map_position+1, ". track piece of the map"
                )
            pass
    finally:
        await vehicle.disconnect()
        pass
    pass

# Only running the main function when actually executing this program
if __name__ == "__main__": asyncio.run(main())