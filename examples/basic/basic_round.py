"""
This example demonstrates the basic setup for single-vehicle programs.
It connects to a non-charging vehicle, drives along the track until it reaches the finish, and then disconnects cleanly.
"""

import anki, asyncio
from anki.utility.const import TrackPieceTypes

# Because we're in an async-context, we need a main function
async def main():
    controller = anki.Controller() # This object handles all the connections to the vehicles

    vehicle = await controller.connectOne() # This object represents the vehicle and is used to control it.

    finished = [False]
    await vehicle.setSpeed(300) # Accelerate the vehicle to 300mm/s
    def watcher(): # Function to check if the vehicle is on the Finish-piece
        track = vehicle._current_track_piece
        print(track)
        if track.type == TrackPieceTypes.FINISH:
            finished[0] = True
        else:
            pass
    vehicle.on_track_piece_change = watcher # Asing the watcher function to the method that jets executed when the track-piece changes
    while not finished[0]:
        await asyncio.sleep(1)
        pass
    await vehicle.stop() # Stop the vehicle
    await vehicle.disconnect() # Always disconnect the vehicle. Otherwise it may bug into a state where it won't reconnect.
    pass

# Only running the main function when actually executing this program
if __name__ == "__main__": asyncio.run(main())