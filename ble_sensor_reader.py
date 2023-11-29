import argparse
import asyncio
import logging
import time
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

async def connect_arduino(name="Nano 33 IoT", macos_use_bdaddr=False):
    print("starting scan...")

    device = await BleakScanner.find_device_by_name(
        name, cb=dict(use_bdaddr=macos_use_bdaddr)
    )
    if device is None:
        print("could not find device with name '%s'", name)
        return

    print("connecting to device...")
    print(device)
    return device

async def read_imu(user_input, device):
    async with BleakClient(device) as client:
        while True:
            data = await client.read_gatt_char("00002745-0000-1000-8000-00805f9b34fb")
            #print(f"Received value: {user_input}")
            # Update user_input based on the received BLE value
            user_input = int.from_bytes(data, byteorder="big")
            print(user_input)
            #await asyncio.sleep(0.1)

async def run():
    user_input = 0
    p1_controller = await connect_arduino()
    p2_controller = await connect_arduino(name="Player 2 Nano")
    await read_imu(user_input, p1_controller)
    await read_imu(user_input, p2_controller)

if __name__ == "__main__":
    asyncio.run(run())
