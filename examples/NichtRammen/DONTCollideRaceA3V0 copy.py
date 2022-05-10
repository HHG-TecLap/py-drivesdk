import sys, os
sys.path.append(os.getcwd())

import anki, asyncio, shiftRegister

intersect1 = shiftRegister.shiftRegister()
intersect2 = shiftRegister.shiftRegister()

control = anki.Controller()


async def Main():
    auto1 = await control.connectOne(1)
    auto2 = await control.connectOne(2)
    auto3 = await control.connectOne(3)

    CarDict = {
        1: auto1,
        2: auto2,
        3: auto3
    }
    await control.scan()

    carOnMap : list[shiftRegister.shiftRegister] = []
    for i in range(len(control.map)):
        carOnMap.append(shiftRegister.shiftRegister())


    def registering(vehicle : anki.Vehicle, ID):
        def regIntern ():
            track = vehicle.current_track_piece
            
            if vehicle.map_position in (2,8):
                intersect1.addNew(ID)
            elif vehicle.map_position not in (2,8) and intersect1.read() == ID:
                intersect1.remove()

            if vehicle.map_position in (3,11):
                intersect2.addNew(ID)
            elif vehicle.map_position not in (3,11) and intersect2.read() == ID:
                intersect2.remove()
            
            carOnMap[vehicle.map_position].addNew(ID)
            if carOnMap[vehicle.map_position-1].read() == ID:
                carOnMap[vehicle.map_position - 1].remove()
        return regIntern

    auto1.on_track_piece_change = registering(auto1,1)
    auto2.on_track_piece_change = registering(auto2,2)
    auto3.on_track_piece_change = registering(auto3,3)


    await auto1.setSpeed(300)
    await auto2.setSpeed(300)
    await auto3.setSpeed(300)
    


    async def carControl(vehicle, id, speed):
        while True:
            if (intersect1.read() not in (0,id)) & (vehicle.map_position in(2,8)):
                if (carOnMap[vehicle.map_position].read() not in (0,id)):
                    await vehicle.setSpeed(CarDict[carOnMap[vehicle.map_position].read()].speed, 100 )
                    while carOnMap[vehicle.map_position].read() not in (0,id):
                        await asyncio.sleep(0)
                else:
                    await vehicle.setSpeed(speed)
                    await vehicle.stop()
                    while intersect1.read() not in (0,id):
                        await asyncio.sleep(0)
                    await vehicle.setSpeed(speed)
            if (intersect2.read() not in (0,id)) & (vehicle.map_position in(3,11)):
                if (carOnMap[vehicle.map_position].read() not in (0,id)):
                    await vehicle.setSpeed(CarDict[carOnMap[vehicle.map_position].read()].speed, 100 )
                    while carOnMap[vehicle.map_position].read() not in (0,id):
                        await asyncio.sleep(0)
                    await vehicle.setSpeed(speed)
                else:
                    await vehicle.stop()
                    while intersect2.read() not in (0,id):
                        await asyncio.sleep(0)
                    await vehicle.setSpeed(speed)
            if (carOnMap[vehicle.map_position].read() not in (0,id)):
                await vehicle.setSpeed(CarDict[carOnMap[vehicle.map_position].read()].speed, 100 )
                while carOnMap[vehicle.map_position].read() not in (0,id):
                    await asyncio.sleep(0)
                await vehicle.setSpeed(speed)
            await asyncio.sleep(0)


    asyncio.create_task(carControl(auto3, 3, 300))
    asyncio.create_task(carControl(auto2, 2, 400))
    asyncio.create_task(carControl(auto1, 1, 200))




    try:
        while True:
            await asyncio.sleep(1)
            #print(carOnMap[15].out(), carOnMap[16].out(), carOnMap[0].out(), carOnMap[1].out(), carOnMap[2].out())
            #print (auto1.map_position, auto2.map_position, auto3.map_position)
            pass
    finally:
        await control.disconnectAll()
        pass
    pass

try: asyncio.run(Main()) 
finally:
        asyncio.run(control.disconnectAll())
