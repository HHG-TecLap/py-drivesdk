"""
This example demonstrates the lane feature.
After connecting to the vehicle, it loops through every one of the lanes marked on the track.
After that it stops the vehicle and disconnects.

There are two lane presets implemented in the library:
    There is Lane3, which offers a LEFT, MIDDLE, and RIGHT lane
    and there is Lane4, which offers LEFT_2, LEFT_1, RIGHT_1, RIGHT_2.
Here, these are ordered left-to-right.
"""

import asyncio
import anki


async def main():
    # Create the Controller managing all connections to the vehicles
    controller = anki.Controller()
    # Connect to one non-charging vehicle
    vehicle = await controller.connect_one()
    # Accelerate to 300mm/s
    await vehicle.set_speed(300)

    # Looping through all type 4 lanes
    for lane in anki.Lane4:
        print("Moving to lane", lane)
        # Changing to a new lane with a horizontal speed of 150mm/s
        await vehicle.change_lane(lane, 150)
        await asyncio.sleep(3)

    await vehicle.stop()
    # Disconnecting from the vehicle after the demo script is complete
    await vehicle.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
