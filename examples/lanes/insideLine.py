import sys, os
sys.path.append(os.getcwd())

import anki, asyncio
from anki.utility.lanes import Lane4

control = anki.Controller()

async def Main():
    auto1 = await control.connect_one()
    #await control.scan()
    print("Ready")
    await auto1.set_speed(300)
    await asyncio.sleep(2)
    print(auto1.current_lane4)
    print(auto1.road_offset)
    await auto1.change_lane(Lane4.LEFT_2)
    await asyncio.sleep(2)
    print(auto1.current_lane4)
    print(auto1.road_offset)
    await auto1.change_lane(Lane4.RIGHT_2)
    await asyncio.sleep(2)
    print(auto1.current_lane4)
    print(auto1.road_offset)
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await control.disconnect_all()





asyncio.run(Main()) 
