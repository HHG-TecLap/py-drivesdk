import anki, asyncio
from aioconsole import ainput

async def main():
    controller = anki.Controller()

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
        for v in vehicles:
            await v.setSpeed(300)
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