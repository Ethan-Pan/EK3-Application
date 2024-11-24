import asyncio
from bleak import BleakScanner, BleakClient

# 定义要连接的设备名称
DEVICE_NAME = "ESP32_BLE_Test"
DEVICE_ADDRESS = "24:DC:C3:90:57:1E"

# 定义要发送的字符串
MESSAGE = "hello world"

# 定义发送消息的间隔时间（秒）
SEND_INTERVAL = 3

# 定义 UUID（根据实际情况修改）
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

async def scan_for_device():
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == DEVICE_NAME and d.address == DEVICE_ADDRESS:
            print(f"Found device: {d.name} ({d.address})")
            return d.address
    print("Device not found")
    return None

async def send_message(client):
    while True:
        await client.write_gatt_char(CHARACTERISTIC_UUID, MESSAGE.encode())
        print(f"Sent: {MESSAGE}")
        await asyncio.sleep(SEND_INTERVAL)

def notification_handler(sender, data):
    print(f"Received: {data.decode()}")

async def main():
    print("Scanning for device...")
    device_address = await scan_for_device()
    if device_address is None:
        return

    print(f"Connecting to device: {device_address}")
    async with BleakClient(device_address) as client:
        print("Connected to device")

        # 启动通知监听
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        print(f"Listening for notifications on {CHARACTERISTIC_UUID}")

        # 发送消息
        await send_message(client)

if __name__ == "__main__":
    asyncio.run(main())
