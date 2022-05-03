import os, sys
sys.path.append(os.getcwd())

import anki, asyncio, pygame
from anki import TrackPieceTypes
import threading

os.chdir(os.path.dirname(os.path.abspath(__file__)))

control = anki.Controller()
async def main():
    auto = await control.connectOne()
    await control.scan(False
    await  auto.setSpeed(300)
    while True:
        for i in range(len(control.map)):
            if auto.current_track_piece is control.map[i]:
                print(i)
            else:
                print("Not", i, auto.map_position)
        await asyncio.sleep(1)

asyncio.run(main())