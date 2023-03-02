"""
This example demonstrates the lane feature.
After connecting to the vehicle, it loops through every one of the lanes marked on the track.
After that it stops the vehicle and disconnects.

There are two lane presets implemented in the library:
    There is Lane3, which offers a LEFT, MIDDLE, and RIGHT lane
    and there is Lane4, which offers LEFT_2, LEFT_1, RIGHT_1, RIGHT_2.
Here, these are ordered left-to-right.
"""

import anki, asyncio

async def main():
    controller = anki.Controller() # Create the Controller managing all connections to the vehicles
    vehicle = await controller.connect_one() # Connect to one non-charging vehicle
    
    await vehicle.set_speed(300) # Accelerate to 300mm/s

    for lane in anki.Lane4: # Looping through every one of the type 4 lanes
        print("Moving to lane",lane)
        await vehicle.change_lane(lane,150) # Changing to a new lane with a horizontal speed of 150mm/s
        await asyncio.sleep(3)
        pass

    await vehicle.stop()
    await vehicle.disconnect() # Disconnecting from the vehicle after the demo script is complete
    pass

if __name__ == "__main__": asyncio.run(main())