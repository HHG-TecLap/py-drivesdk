import bleak, asyncio
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import bleak.backends.service
import bleak.utils
from const import *
from utils import interpretLocalName
import aioconsole

import logging
logging.basicConfig()


"""Anki Advertisement:
Has an ANKI_SERVICE_UUID
Local Name:
    1. Byte: Battery State (See const.BatteryStates)
    2. Byte: Firmware Version (some byte \x01-\x7f)
    Remaining:
        Name of the device terminated by \x00 byte
        Up to 17 characters (not including terminator)
        May also just be a NULL_TERMINATOR
"""

async def findOne(scanner : bleak.BleakScanner, timeout : float = 10) -> BLEDevice:
    def isAnki(device : BLEDevice, advertisement : AdvertisementData):
        ankiFound = False
        for service_uuid in advertisement.service_uuids:
            ankiFound = (service_uuid.lower() == SERVICE_UUID)
            if ankiFound: break
            pass
        return ankiFound
        pass
    device = await scanner.find_device_by_filter(isAnki,timeout=timeout)

    return device
    pass

async def findAll(scanner : bleak.BleakScanner, timeout : float = 5) -> list[BLEDevice]:
    rawDevices = await scanner.discover(timeout=timeout)
    return [device for device in rawDevices if SERVICE_UUID in device.metadata.get("uuids")]
    pass


async def main():
    scanner = bleak.BleakScanner()

    devices = await findAll(scanner,1)

    i = 0
    while i < len(devices):
        print(i,":",devices[i])
        i += 1
        pass

    while True:
        valid = True
        try:
            res : str = await aioconsole.ainput("Please select one of the devices above: ")
            res = int(res)
        except ValueError:
            valid = False
            pass
        if valid:
            valid = res < len(devices) and res >= 0
            pass

        if not valid:
            print("This is not a valid input, try again")
            continue
        else:
            break
        pass
    res : int
    print("Selected",interpretLocalName(devices[res].name))
    pass

if __name__=="__main__":
    asyncio.run(main())
    pass
