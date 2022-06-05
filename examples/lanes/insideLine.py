import sys, os
sys.path.append(os.getcwd())

import anki, asyncio
from anki.utility.lanes import Lane4

control = anki.Controller()

async def Main():
    auto1 = await control.connectOne()
    #await control.scan()
    print("Ready")
    await auto1.setSpeed(300)
    await asyncio.sleep(2)
    print(auto1.current_lane4)
    print(auto1.road_offset)
    await auto1.changeLane(Lane4.LEFT_2)
    await asyncio.sleep(2)
    print(auto1.current_lane4)
    print(auto1.road_offset)
    await auto1.changeLane(Lane4.RIGHT_2)
    await asyncio.sleep(2)
    print(auto1.current_lane4)
    print(auto1.road_offset)
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await asyncio.gather([await v.disconnect() for v in control.vehicles])





asyncio.run(Main()) 
