import asyncio
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError
from . import ek_keyboard
from . import weather
from PySide6.QtCore import QThread, Signal
import asyncio.events
import sys, os

class BLEThread(QThread):
    message_received = Signal(str)  # 用于向GUI发送消息的信号
    connection_status = Signal(bool)  # 用于向GUI发送连接状态的信号

    def __init__(self, ble_manager):
        super().__init__()
        self.ble_manager = ble_manager
        self.running = True
        self.config_dir = os.path.join(os.path.expanduser('~'), '.ek3')
        self.config_file = os.path.join(self.config_dir, 'ek3.config')

    def run(self):
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.async_run())
        finally:
            loop.close()

    def stop(self):
        self.running = False

    async def async_run(self):
        await self.ble_manager.connect()
        try:
            while self.running:
                if self.ble_manager.first_connect == 0:
                    self.ble_manager.send_interval = 2
                else:
                    self.ble_manager.send_interval = 60
                
                message = self.ble_manager.update_message()
                await self.ble_manager.send_message(message)
                self.message_received.emit(message)  # 发送消息到GUI
                self.connection_status.emit(self.ble_manager.is_connected)  # 发送连接状态到GUI
                
                await asyncio.sleep(self.ble_manager.send_interval)
        except Exception as e:
            print(f"BLE Thread error: {e}")
        finally:
            await self.ble_manager.disconnect()

class BLEDeviceManager:
    def __init__(self):
        self.device_address = self.get_ble_address()
        self.characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
        self.send_interval = 60
        self.client = None
        self.is_connected = False
        self.first_connect = 0
        self.keyboard = ek_keyboard.Keyboard()
        self.message = weather.WeatherAPI(self.get_area())
        self.thread = None

    async def scan_for_device(self):
        devices = await BleakScanner.discover()
        for d in devices:
            if d.address == self.device_address:
                print(f"Found device: {d.name} ({d.address})")
                return d.address
        print("Device not found")
        return None

    async def connect(self):
        try:
            print("Scanning for device...")
            device_address = await self.scan_for_device()
            while device_address is None:
                print("重新扫描设备...")
                await asyncio.sleep(3)
                device_address = await self.scan_for_device()

            print(f"Connecting to device: {device_address}")
            if self.client:
                await self.client.disconnect()
            
            self.client = BleakClient(device_address)
            self.client.disconnected_callback = self.disconnect_callback
            await self.client.connect()
            print("Connected to device")
            self.is_connected = True
            await self.listen()
        except BleakError as e:
            print(f"Connection error: {e}")
            self.is_connected = False
            await self.reconnect()

    async def listen(self):
        try:
            await self.client.start_notify(self.characteristic_uuid, self.notification_handler)
        except BleakError as e:
            print(f"Notification error: {e}")
            await self.reconnect()

    async def send_message(self, message):
        try:
            if not self.is_connected:
                print("Not connected, attempting to reconnect...")
                await self.connect()
            await self.client.write_gatt_char(self.characteristic_uuid, message.encode())
            self.first_connect = 1
            print(f"Sent: {message}")
        except BleakError as e:
            print(f"Send message error: {e}")
            self.is_connected = False
            self.first_connect = 0
            await self.reconnect()

    def notification_handler(self, sender, data):
        print(f"Received: {data.decode()}")
        self.keyboard_event(data.decode())

    async def reconnect(self):
        if not self.is_connected:
            self.first_connect = 0
            print("Starting reconnection process...")
            retry_count = 0
            max_retries = 10
            
            while not self.is_connected and retry_count < max_retries:
                try:
                    print(f"Reconnection attempt {retry_count + 1}/{max_retries}")
                    await self.connect()
                except Exception as e:
                    print(f"Reconnection failed: {e}")
                    retry_count += 1
                    await asyncio.sleep(5)
            
            if not self.is_connected:
                print("Max reconnection attempts reached")

    def disconnect_callback(self, client):
        print(f"Disconnect callback triggered for {self.device_address}")
        self.is_connected = False
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(self.reconnect())
            else:
                asyncio.run(self.reconnect())
        except Exception as e:
            print(f"Error in disconnect callback: {e}")

    def keyboard_event(self, key):
        if key == "$221#":
            self.keyboard.volume_up()
        elif key == "$222#":
            self.keyboard.volume_down()
        elif key == "$223#":
            self.keyboard.volume_mute()
        elif key == "$224#":
            self.keyboard.volume_no_mute()
        elif key == "$225#":
            self.keyboard.next_music()
        elif key == "$226#":
            self.keyboard.prev_music()
        elif key == "$227#":
            self.keyboard.music_play()
        elif key == "$228#":
            self.keyboard.music_pause()
        elif key == "$111#":
            self.keyboard.finger_up('a10030928')
    
    def update_message(self):
        return self.message.get_weather_data()

    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            self.is_connected = False
            print("Disconnected from device")

    def get_ble_address(self):
        if not os.path.exists(self.config_file):
            return None
        with open(self.config_file, 'r', encoding='utf-8') as f:
            for line in f:
                if 'ble_address' in line:
                    return line.split('=')[1].strip()
        return None

    def get_area(self):
        if not os.path.exists(self.config_file):
            return None
        with open(self.config_file, 'r', encoding='utf-8') as f:
            for line in f:
                if 'area_city' in line:
                    area_city = line.split('=')[1].strip()
                    city_ch_list = ['深圳', '东莞', '广州', '惠州', '中山']
                    city_en_list = ['shenzhen', 'dongguan', 'guangzhou', 'huizhou', 'zhongshan']
                    if area_city in city_ch_list:
                        return city_en_list[city_ch_list.index(area_city)]
                    else:
                        return 'shenzhen'
        return None

    def start_background_task(self):
        if self.thread is None or not self.thread.isRunning():
            self.thread = BLEThread(self)
            self.thread.start()
    
    def stop_background_task(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()  # 等待线程结束

# test
if __name__ == "__main__":
    async def main():
        ble_manager = BLEDeviceManager()
        ble_manager.start_background_task()
        try:
            while True:
                if ble_manager.first_connect == 0:
                    ble_manager.send_interval = 2
                else:
                    ble_manager.send_interval = 60
                print('send_interval:', ble_manager.send_interval, 'first_connect:', ble_manager.first_connect)
                message = ble_manager.update_message()
                await ble_manager.send_message(message)
                await asyncio.sleep(ble_manager.send_interval)  # 等待1分钟
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            ble_manager.stop_background_task()

    asyncio.run(main())
