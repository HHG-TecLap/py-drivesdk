"""
This example demonstrates the basic setup for single-vehicle programs.
It connects to a non-charging vehicle, drives along the track for 10 seconds, and then disconnects cleanly.
"""

import anki, asyncio

# Because we're in an async-context, we need a main function
async def main():
    controller = anki.Controller() # This object handles all the connections to the vehicles

    vehicle = await controller.connect_one() # This object represents the vehicle and is used to control it.

    await vehicle.set_speed(300) # Accelerate the vehicle to 300mm/s
    await asyncio.sleep(10)
    await vehicle.stop() # Stop the vehicle

    await vehicle.disconnect() # Always disconnect the vehicle. Otherwise it may bug into a state where it won't reconnect.
    pass

# Only running the main function when actually executing this program
if __name__ == "__main__": asyncio.run(main())