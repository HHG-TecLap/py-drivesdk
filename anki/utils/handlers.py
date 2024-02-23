from time import monotonic
import asyncio
import logging

from ..control.vehicle import Vehicle
from .references import Reference

__all__ = (
    "recover_delocalization",
)

async def _handle_delocalization_task(
        v: Vehicle,
        tracker: Reference[float],
        recovery_speed: int|None
    ):
    if recovery_speed is None:
        recovery_speed = v.speed
    await v.stop()
    logging.debug("Automatic delocalization recovery stopped vehicle")
    while monotonic()-tracker.value < 2:
        logging.info("Vehicle still delocalized")
        await asyncio.sleep(2)
        logging.debug("Attempting to recover from delocalization...")
    await v.set_speed(recovery_speed)
    logging.debug("Recovery successful. Vehicle restarted")

def recover_delocalization(v: Vehicle, recovery_speed: int|None=None):
    task: asyncio.Task|None = None
    last_callback = Reference(0.0)
    def callback():
        nonlocal task
        last_callback.value = monotonic()
        if task is None or task.done():
            task = asyncio.create_task(_handle_delocalization_task(v, last_callback, recovery_speed))
        logging.warning("Vehicle has delocalized. Attempting automatic reovery")
    return callback