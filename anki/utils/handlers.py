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

def recover_delocalization(vehicle: Vehicle, recovery_speed: int|None=None):
    """
    Generates and registers a callback that 
    automatically handles a delocalized vehicle.

    It does this by creating a new task when a vehicle is delocalized.
    This task repeatedly checks if the vehicle has **not** send a
    delocalization packages in the last 2 seconds and attempts to restart
    the vehicle in that case. Otherwise it continues to wait.
    
    :param vehicle: :class:`Vehicle`
        The :class:`Vehicle` to register the callback to.
    :param recovery_speed: :class:`Optional[int]`
        The speed with which to recover from delocalization.
        If set to :const:`None`, the task will use the 
        last recorded speed.

        .. note::
            Leaving this value as :const:`None` may gradually
            decrease vehicle speed over long periods of time,
            if speed is not set regularly.
    
    Returns
    -------
    :class:`Callable[[], None]`

    The registered callback. Using this as an argument to
    :func:`Vehicle.remove_delocalized_watcher` will remove
    the automatic delocalization recovery.
    Executing this function will start it.

    .. warn::
        It is highly adviced not to manually start recovery
        unless you are absolutely certain the vehicle has 
        delocalized.
    """
    task: asyncio.Task|None = None
    last_callback = Reference(0.0)
    @vehicle.delocalized
    def callback():
        nonlocal task
        last_callback.value = monotonic()
        if task is None or task.done():
            task = asyncio.create_task(_handle_delocalization_task(
                vehicle,
                last_callback,
                recovery_speed
            ))
        logging.warning("Vehicle has delocalized. Attempting automatic reovery")
    return callback
