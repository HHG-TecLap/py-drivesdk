"""
This example demonstrates the basic-setup for a multi-vehicle program.
Similarly to the basic_single, it connects to **two** vehicles, drives around for 10 seconds and then disconnects clearnly.
"""

import anki, asyncio

# Because we're in an async-context, we need a main function
async def main():
    controller = anki.Controller() # This object handles all the connections to the vehicles

    vehicles = await controller.connectMany(2) # This simplifies connecting to multiple vehicles a lot

    for v in vehicles: # `vehicles` is a tuple, meaning we can iterate over it like this
        await v.setSpeed(300) 
    await asyncio.sleep(10)
    for v in vehicles:
        await v.stop()
        pass

    await controller.disconnectAll() # This is a short hand for disconnecting from multiple vehicles
    pass

# Only running the main function when actually executing this program
if __name__ == "__main__": asyncio.run(main())