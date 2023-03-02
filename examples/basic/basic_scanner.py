"""
This example demonstrates a scanner.
It connects to one vehicle and then drives around the map.
Whilst driving around the track, it creates a map of it and afterwards continues driving and printing out its position.
Use Ctrl+C to disconnect from the vehicle and end the program.
"""


import anki, asyncio

# Because we're in an async-context, we need a main function
async def main():
    controller = anki.Controller() # This object handles all the connections to the vehicles

    vehicle = await controller.connect_one()
    
    await controller.scan() # This will make your vehicle scan in the whole track traversing all of it and aligning to the start field with it
    # Running this function is also necessary for you to use properties like vehicle.map, vehicle.map_position, and vehicle.current_track_piece

    await vehicle.set_speed(300) # Accelerating the vehicle to a speed of 300mm/s

    # The try-finally combination means that this code will always disconnect the vehicle before it exits.
    # It is not required, but definitely recommended to prevent vehicles staying in a semi-connected mode where they won't connect again.
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