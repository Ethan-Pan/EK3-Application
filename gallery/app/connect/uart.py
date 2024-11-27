import serial
import serial.tools.list_ports
import time
from PySide6.QtCore import QThread, Signal
import os
from . import weather
from . import ota
import threading

class FingerEnrollThread(QThread):
    finished = Signal(int)  # 信号用于通知录入结果：1成功，0失败，-1异常

    def __init__(self, uart, finger_id):
        super().__init__()
        self.uart = uart
        self.finger_id = finger_id

    def run(self):
        try:
            self.uart.ser.write(('#01'+str(self.finger_id)+'$').encode())
            
            # 循环检查响应，最多等待12秒
            for _ in range(24):  # 24 * 0.5s = 12s
                time.sleep(0.5)
                if self.uart.listen_open and self.uart.receive_ack:
                    self.uart.receive_ack = False
                    response = self.uart.response
                    print(f'enroll response:{response}')
                    if 'ok' in response:
                        self.uart.response = None
                        self.uart.connected = True
                        self.finished.emit(1)
                        return
                    if '$000#' in response:
                        self.uart.response = None
                        self.uart.connected = True
                        self.finished.emit(0)
                        return                    
                    if '$003#' in response:
                        self.uart.response = None
                        self.uart.connected = True
                        self.finished.emit(-1)
                        return
            
            # 超时处理
            self.finished.emit(-1)
            
        except Exception as e:
            print(f"指纹录入异常: {e}")
            self.finished.emit(-1)

class UartListenThread(QThread):
    message_received = Signal(str)  # 用于向GUI发送消息的信号
    def __init__(self, uart):
        super().__init__()
        self.uart = uart 
        self.running = True

    def run(self):
        while self.running:
            try:
                if self.uart.ser and self.uart.ser.in_waiting:
                    response = self.uart.ser.read(self.uart.ser.in_waiting).decode().strip()
                    self.message_received.emit(response)
                self.msleep(300)
            except Exception as e:
                print(f"串口监听异常: {e}")
                self.uart.connected = False
                self.uart.try_connect(stop=False)
                self.msleep(3000)
    
    def delayms(self, ms):
        self.msleep(ms)
    
    def stop(self):
        self.uart.listen_open = False
        self.running = False

class UartConnect():
    def __init__(self):
        self.port = None
        self.ser = None
        self.connected = False
        self.enroll_thread = None
        self.weather = None
        self.listen_open = False
        self.receive_ack = False
        self.response = None
        self.ota = ota.Ota()
        self.last_connect_time = None
        # self.connect_port('COM3')
        self.config_dir = os.path.join(os.path.expanduser('~'), '.ek3')
        self.config_file = os.path.join(self.config_dir, 'ek3.config')
        self.first_connect_flag = os.path.exists(self.config_file)

        if self.first_connect_flag:
            if not self.check_connection():
                print('try connect')
                if self.try_connect():
                    self.connected = True
                    self.run_uart_listen()
            elif not self.listen_open:
                print('run uart listen')
                self.connected = True
                self.run_uart_listen()



    def run_uart_listen(self):
        print('uart listen is open')
        self.uarthread = UartListenThread(self)
        self.uarthread.message_received.connect(self.handle_message)
        self.uarthread.start()
        self.listen_open = True
        return self.uarthread

    def handle_message(self, message):
        print(f'uart handle_message:{message}')
        self.response = message
        self.listen_open = True
        self.connected = True
        if 'AT+WEATHER' in message:
            self.wire_update_weather()
            self.receive_ack = False
            self.response = None
            
        if 'AT+VERSION' in message:
            self.wire_check_version(message)
            self.receive_ack = False
            self.response = None
        
        if 'AT+UPDATE' in message:
            self.wire_update_firmware()
            self.receive_ack = False
            self.response = None

        if 'AT+CONNECT' in message:
            self.connected = True
            self.last_connect_time = time.time()
            
    def wire_check_version(self, message):
        cur_version = message.split('+VERSION:')[1].strip()
        lastest_version = self.ota.check_version('EK3-firmware')
        if cur_version != lastest_version:
            self.ser.write(('#0a1'+lastest_version+'$').encode())
        else:
            self.ser.write(('#0a0$').encode())
    
    def wire_update_firmware(self):
        self.ota.downLoad()
        self.ota.flash_firmware(self.port)


    def scan_ports(self):
        """扫描所有串口并返回包含'CH340'的端口列表"""
        ports = []
        for p in serial.tools.list_ports.comports():
            if 'CH340' in p.description:
                ports.append(p.device)
        return ports
        
    def connect_port(self, port):
        """尝试连接指定串口"""
        try:
            self.ser = None
            self.ser = serial.Serial(
                port=port,
                baudrate=115200,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
            self.port = port
            return True
        except:
            return False
            
    def disconnect(self):
        """断开当前连接"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None
        self.port = None
        self.connected = False
    
    def check_connection(self):
        if self.listen_open:
            self.uarthread.stop()
        """检测当前连接的串口是否断开"""
        if not self.connected or not self.ser:
            return False
        if self.connected:
            try:
                self.ser.write('#001$'.encode())
                time.sleep(0.3)
                if self.ser.in_waiting:
                    response = self.ser.readline().decode().strip()
                    if response:
                        print(f'check_connection response:{response}')
                        self.connected = True
                        return True
                self.disconnect()
                return False
            except:
                # 发生异常说明连接已断开
                self.disconnect() 
                return False
        else:
            return True

    def try_connect(self, stop=True):
        if self.listen_open and stop:
            self.uarthread.stop()
        # 扫描所有CH340串口
        ch340_ports = self.scan_ports()
        print(f"当前设备：{ch340_ports}")
        if not ch340_ports:
            print("未找到CH340串口设备")
            return False
            
        # 依次尝试每个串口
        for port in ch340_ports:
            print(f"尝试连接串口: {port}")
            
            # 连接串口
            if not self.connect_port(port):
                print(f"无法打开串口 {port}")
                continue

            # 发送测试命令
            try:
                self.ser.write('#001$'.encode())
                time.sleep(1)  # 等待响应
                if self.ser.in_waiting:
                    response = self.ser.readline().decode().strip()
                    if response:
                        self.connected = True
                        return True
            except:
                return False
                
            # 未收到正确响应，断开连接
            print(f"串口 {port} 未收到正确响应")
            self.disconnect()
            
        print("未找到可用设备")
        return False

    def finger_enroll(self, id):
        # 创建并启动录入线程
        self.enroll_thread = FingerEnrollThread(self, id)
        self.enroll_thread.start()
        return self.enroll_thread  # 返回线程对象以便连接信号

    def finger_delete(self, id):
        if self.listen_open:
            self.uarthread.exit()
            self.listen_open = False
        # 发送测试命令
        try:
            time.sleep(0.1)
            # 在发送前先清空缓冲区
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.write(('#02'+str(id)+'$').encode())
            time.sleep(1)  # 等待响应
            
            if self.ser.in_waiting:
                response = self.ser.readline().decode().strip()
                if response:
                    self.connected = True
                    return 1
        except:
            return -1
    
    def send_command(self, command):
        if self.listen_open:
            self.uarthread.stop()
        try:
            self.ser.write(command.encode())
            time.sleep(0.8)  # 等待响应
            
            if self.ser.in_waiting:
                response = self.ser.readline().decode().strip()
                if response:
                    self.connected = True
                    return 1
                else:
                    return 0
        except:
            return -1
    
    def get_ble_address(self, command):
        if self.listen_open:
            self.uarthread.stop()
            self.listen_open = False
        try:
            time.sleep(0.1)
            # 在发送前先清空缓冲区
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.write(command.encode())
            time.sleep(3)  # 等待响应
            
            if self.ser.in_waiting:
                response = self.ser.readline().decode().strip()
                if 'BLE Address' in response:
                    self.connected = True
                return response
            else:
                return 0
        except:
            return -1

    def get_weather_API(self):
        if not os.path.exists(self.config_file):
            return None
        area_city = ['深圳', '东莞', '广州', '惠州', '中山']
        area_city_en_list = ['shenzhen', 'dongguan', 'guangzhou', 'huizhou', 'zhongshan']
        with open(self.config_file, 'r', encoding='utf-8') as f:
            for line in f:
                if 'area_city' in line:
                    city = line.split('=')[1].strip()
                    index = area_city.index(city)
                    return weather.WeatherAPI(area_city_en_list[index])
                
    # update the config
    def updateConfig(self, config_data, connect_flag):
        flag = 0
        update_count = 0
        # 读取现有配置
        config_dict = {'user_name':None, 'area_city':None, 'power_show':None, 'encoder':None, 'color':None, 'power_save_start':None, 'power_save_end':None, 'power_deep_save':None, 'finger_pin':None, 'x_mode':None, 'x_input':None, 'update':None, 'connect':None}
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=')
                        config_dict[key] = value
        # user name
        if config_data['user_name'] != config_dict['user_name']:
            comand = '#040' + config_data['user_name'] + '$'
            flag += self.send_command(comand)
            print(f'user name:{comand},flag:{flag}')
            update_count += 1
        # area city
        area_city = ['深圳', '东莞', '广州', '惠州', '中山']
        area_city_en = ['Shen Zhen', 'Dong Guan', 'Guang Zhou', 'Hui Zhou', 'Zhong Shan']
        area_city_en_list = ['shenzhen', 'dongguan', 'guangzhou', 'huizhou', 'zhongshan']
        if config_data['area_city'] != config_dict['area_city']:
            index = area_city.index(config_data['area_city'])
            self.weather = weather.WeatherAPI(area_city_en_list[index])
            comand = '#041' + area_city_en[index] + '$'
            flag += self.send_command(comand)
            print(f'area city:{comand},flag:{flag}')
            update_count += 1
        # power show
        if config_data['power_show'] != config_dict['power_show']:
            comand = '#042' + str(config_data['power_show']) + '$'
            flag += self.send_command(comand)
            print(f'power show:{comand},flag:{flag}')
            update_count += 1   
        # encoder
        if config_data['encoder'] != config_dict['encoder']:
            comand = '#043' + str(config_data['encoder']) + '$'
            flag += self.send_command(comand)
            print(f'encoder:{comand},flag:{flag}')
            update_count += 1
        # color
        if config_data['color'] != config_dict['color']:
            comand = '#044' + str(config_data['color']) + '$'
            flag += self.send_command(comand)
            print(f'color:{comand},flag:{flag}')
            update_count += 1
        # power save start
        if config_data['power_save_start'] != config_dict['power_save_start']:
            comand = '#045' + str(config_data['power_save_start']) + '$'
            flag += self.send_command(comand)
            print(f'power save start:{comand},flag:{flag}')
            update_count += 1
        # power save end
        if config_data['power_save_end'] != config_dict['power_save_end']:
            comand = '#046' + str(config_data['power_save_end']) + '$'
            flag += self.send_command(comand)
            print(f'power save end:{comand},flag:{flag}')
            update_count += 1
        # power deep save
        if config_data['power_deep_save'] != config_dict['power_deep_save']:
            comand = '#047' + str(config_data['power_deep_save']) + '$'
            flag += self.send_command(comand)
            print(f'power deep save:{comand},flag:{flag}')
            update_count += 1
        # finger pin
        if config_data['finger_pin'] != config_dict['finger_pin']:
            comand = '#048' + str(config_data['finger_pin']) + '$'
            flag += self.send_command(comand)
            print(f'finger pin:{comand},flag:{flag}')
            update_count += 1
        # x mode
        if config_data['x_mode'] != config_dict['x_mode']:
            comand = '#049' + str(config_data['x_mode']) + '$'
            flag += self.send_command(comand)
            print(f'x mode:{comand},flag:{flag}')
            update_count += 1
        # x input
        if config_data['x_input'] != config_dict['x_input']:
            comand = '#04a' + str(config_data['x_input']) + '$'
            flag += self.send_command(comand)
            print(f'x input:{comand},flag:{flag}')
            update_count += 1
        # update flag
        if config_data['update'] != config_dict['update']:
            comand = '#04b' + str(config_data['update']) + '$'
            flag += self.send_command(comand)
            print(f'update flag:{comand},flag:{flag}')
            update_count += 1
        # connect flag
        if config_data['connect'] != config_dict['connect']:
            comand = '#04c' + str(config_data['connect']) + '$'
            flag += self.send_command(comand)
            print(f'connect flag:{comand},flag:{flag}')
            update_count += 1
        # ble connect
        if connect_flag == '2':
            command = '#070$'
            response = self.get_ble_address(command)
            if 'BLE Address' in response:
                address = response.split('BLE Address:')[1].strip()
                print(f'ble address:{address}')
                self.add_ble_address(address)

        print(f'uart updateConfig flag:{flag}, update_count:{update_count}')
        if flag >= update_count:
            # 发送重启命令
            command = '#060$'
            self.send_command(command)
            return 1
        else:
            return 0

    def wire_update_weather(self):
        if self.listen_open:
            self.uarthread.exit()
            self.listen_open = False
         # wire connect
        try:
            if self.weather is None:
                self.weather = self.get_weather_API()
            weather_data = self.weather.get_weather_data()
            comand = '#080' + weather_data + '$'
            print(f'weather command:{comand}')
            self.ser.write(comand.encode())
            time.sleep(1)
            if self.ser.in_waiting:
                response = self.ser.readline().decode().strip()
                if response:
                    self.connected = True
                    return 1
                else:
                    return 0
        except:
            self.try_connect()
            return -1

    def add_ble_address(self, address):
        if not os.path.exists(self.config_file):
            return 0
        config_dict = {}
        with open(self.config_file, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=')
                    config_dict[key] = value
                    
        config_dict['ble_address'] = address
        
        # 写回文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            for key, value in config_dict.items():
                f.write(f"{key}={value}\n")

if __name__ == '__main__':
    test = UartConnect()
    test.add_ble_address('AC:15:18:C0:D9:7A')
