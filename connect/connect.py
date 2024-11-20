import asyncio
import json
from bleak import BleakScanner, BleakClient

TARGET_DEVICE_NAME = "ESP32_BLE_Test"

async def scan_for_devices():
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Device {device.name}: {device.address}")
    return devices

async def connect_and_send_data(device_name):
    devices = await scan_for_devices()
    target_device = None

    for device in devices:
        if device.name == device_name:
            target_device = device
            break

    if target_device is None:
        print(f"No device with name {device_name} found.")
        return

    async with BleakClient(target_device.address) as client:
        connected = await client.is_connected()
        if connected:
            print(f"Connected to {device_name} at address {target_device.address}")
            # Prepare JSON data
            data = json.dumps({"temperature": 23, "humidity": 45})
            # You need to specify the correct characteristic UUID here:
            # This is just a placeholder UUID
            characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
            await client.write_gatt_char(characteristic_uuid, data.encode())
            print("Data sent")
        else:
            print("Failed to connect.")

def main():
    asyncio.run(connect_and_send_data(TARGET_DEVICE_NAME))

if __name__ == "__main__":
    main()
