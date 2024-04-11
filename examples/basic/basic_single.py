"""
This example demonstrates the basic setup for single-vehicle programs.
It connects to a non-charging vehicle, drives along the
track for 10 seconds, and then disconnects cleanly.
"""

import asyncio
import anki


# Because we're in an async-context, we need a main function
async def main():
    # This object handles all the connections to the vehicles
    controller = anki.Controller()

    # This object represents the vehicle and is used to control it.
    vehicle = await controller.connect_one()

    # Accelerate the vehicle to 300mm/s, wait 10 seconds, then stop again
    await vehicle.set_speed(300)
    await asyncio.sleep(10)
    await vehicle.stop()

    # Always disconnect the vehicle. Otherwise it may bug into a state where it won't reconnect.
    await vehicle.disconnect()

# Only running the main function when actually executing this program
if __name__ == "__main__":
    asyncio.run(main())
