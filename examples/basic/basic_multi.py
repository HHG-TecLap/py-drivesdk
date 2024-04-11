"""
This example demonstrates the basic-setup for a multi-vehicle program.
Similarly to the basic_single, it connects to **two** vehicles,
drives around for 10 seconds and then disconnects clearnly.
"""

import asyncio
import anki


# Because we're in an async-context, we need a main function
async def main():
    # This object handles all the connections to the vehicles
    controller = anki.Controller()
    # This simplifies connecting to multiple vehicles a lot
    vehicles = await controller.connect_many(2)

    # `vehicles` is a tuple, meaning we can iterate over it like this
    for v in vehicles:
        await v.set_speed(300)
    await asyncio.sleep(10)
    for v in vehicles:
        await v.stop()

    # This is a short hand for disconnecting from multiple vehicles
    await controller.disconnect_all()

# Only running the main function when actually executing this program
if __name__ == "__main__":
    asyncio.run(main())
