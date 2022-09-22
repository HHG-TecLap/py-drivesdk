"""
This example expands upon basic_single. 
Here, the vehicle drives 1 round of the track, before stopping.
The concept of vehicle alignment and the `Vehicle.wait_for_track_change` method are demonstrated.
"""

import anki, asyncio
from anki.utility.const import TrackPieceTypes

# Because we're in an async-context, we need a main function
async def main():
    controller = anki.Controller() # This object handles all the connections to the vehicles

    vehicle = await controller.connectOne() # This object represents the vehicle and is used to control it.
    
    await vehicle.align() # Align to the START piece. This will allow us to use Vehicle.map_position later
    await vehicle.setSpeed(300) # Accelerate the vehicle to 300mm/s

    await vehicle.wait_for_track_change() # Wait for the vehicle to reach a new position.
    # We do this once before the loop so that we leave the START piece before checking if we are on the piece.
    while vehicle.map_position == 0: # This while-loop runs until the vehicle is at position 0, which is always the START piece.
        print("The vehicle is currently on position",vehicle.map_position) # Print out the current position of the vehicle
        await vehicle.wait_for_track_change() # Wait for the vehicle to reach a new position. 
        # We won't actually get a track piece out of this since the map is not scanned in.
        pass
    
    await vehicle.stop() # Stop the vehicle
    await vehicle.disconnect() # Always disconnect the vehicle. Otherwise it may bug into a state where it won't reconnect.
    pass

# Only running the main function when actually executing this program
if __name__ == "__main__": asyncio.run(main())