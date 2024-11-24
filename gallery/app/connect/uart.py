import serial
import serial.tools.list_ports
import time
from PySide6.QtCore import QThread, Signal
import os
from . import weather

class FingerEnrollThread(QThread):
    finished = Signal(int)  # 信号用于通知录入结果：1成功，0失败，-1异常

    def __init__(self, uart, finger_id):
        super().__init__()
        self.uart = uart
        self.finger_id = finger_id

    def run(self):
        try:
            self.uart.connect_flag = 1
            self.uart.ser.write(('#01'+str(self.finger_id)+'$').encode())
            
            # 循环检查响应，最多等待12秒
            for _ in range(24):  # 24 * 0.5s = 12s
                time.sleep(0.5)
                if self.uart.ser.in_waiting:
                    response = self.uart.ser.read(self.uart.ser.in_waiting).decode()
                    print(f'enroll response:{response}')
                    if '$001#' in response:
                        self.uart.connected = True
                        self.uart.connect_flag = 0
                        self.finished.emit(1)
                        return
                    if '$000#' in response:
                        self.uart.connected = True
                        self.uart.connect_flag = 0
                        self.finished.emit(0)
                        return                    
                    if '$003#' in response:
                        self.uart.connected = True
                        self.uart.connect_flag = 0
                        self.finished.emit(-1)
                        return
            
            # 超时处理
            self.uart.connect_flag = 0
            self.finished.emit(-1)
            
        except Exception as e:
            print(f"指纹录入异常: {e}")
            self.uart.connect_flag = 0
            self.finished.emit(-1)

class UartConnect:
    def __init__(self):
        self.port = None
        self.ser = None
        self.connected = False
        self.connect_flag = 0
        self.enroll_thread = None
        self.weather = None
        # self.connect_port('COM3')
        
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
        """检测当前连接的串口是否断开"""
        if not self.connected or not self.ser:
            return False
        if self.connect_flag == 0:
            try:
                time.sleep(0.1)
                 # 在发送前先清空缓冲区
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                # 发送测试命令
                self.ser.write('#001$'.encode())
                time.sleep(0.3)
                
                if self.ser.in_waiting:
                    response = self.ser.read(self.ser.in_waiting).decode()
                    if '$001#' in response:
                        return True
                        
                # 未收到正确响应,说明连接已断开
                self.disconnect()
                return False
                
            except:
                # 发生异常说明连接已断开
                self.disconnect() 
                return False
        else:
            return True

    def try_connect(self):
        """尝试连接所有CH340串口直到找到正确的设备"""
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
                time.sleep(0.1)
                # 在发送前先清空缓冲区
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                self.ser.write('#001$'.encode())
                time.sleep(0.3)  # 等待响应
                
                if self.ser.in_waiting:
                    response = self.ser.read(self.ser.in_waiting).decode()
                    print(f'connect response:{response}')
                    if '$001#' in response:
                        print(f"成功连接到设备，串口: {port}")
                        self.connected = True
                        return True
            except:
                pass
                
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
        # 发送测试命令
        self.connect_flag = 1 
        try:
            time.sleep(0.1)
            # 在发送前先清空缓冲区
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.write(('#02'+str(id)+'$').encode())
            time.sleep(0.5)  # 等待响应
            
            if self.ser.in_waiting:
                response = self.ser.read(self.ser.in_waiting).decode()
                print(f'delete response:{response}')
                if '$001#' in response:
                    self.connected = True
                    self.connect_flag = 0
                    return 1
                if '$000#' in response:
                    self.connect_flag = 0
                    return 0
        except:
            self.connect_flag = 0
            return -1
    
    def send_command(self, command):
        try:
            time.sleep(0.1)
            # 在发送前先清空缓冲区
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.write(command.encode())
            time.sleep(1)  # 等待响应
            
            if self.ser.in_waiting:
                response = self.ser.read(self.ser.in_waiting).decode()
                if '$001#' in response:
                    self.connected = True
                    self.connect_flag = 0
                    return 1
                if '$000#' in response:
                    self.connect_flag = 0
                    return 0
        except:
            self.connect_flag = 0
            return -1
    
    def get_ble_address(self, command):
        try:
            time.sleep(0.1)
            # 在发送前先清空缓冲区
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.write(command.encode())
            time.sleep(3)  # 等待响应
            
            if self.ser.in_waiting:
                response = self.ser.read(self.ser.in_waiting).decode()
                if 'BLE Address' in response:
                    return response
                else:
                    return 0
        except:
            self.connect_flag = 0
            return -1

    # update the config
    def updateConfig(self, config_data, connect_flag):
        flag = 0
        # user name
        comand = '#040' + config_data['user_name'] + '$'
        flag += self.send_command(comand)
        print(f'user name:{comand}')
        # area city
        area_city = ['深圳', '东莞', '广州', '惠州', '中山']
        area_city_en = ['Shen Zhen', 'Dong Guan', 'Guang Zhou', 'Hui Zhou', 'Zhong Shan']
        area_city_en_list = ['shenzhen', 'dongguan', 'guangzhou', 'huizhou', 'zhongshan']
        index = area_city.index(config_data['area_city'])
        self.weather = weather.WeatherAPI(area_city_en_list[index])
        comand = '#041' + area_city_en[index] + '$'
        flag += self.send_command(comand)
        print(f'area city:{comand}')
        # power show
        comand = '#042' + str(config_data['power_show']) + '$'
        flag += self.send_command(comand)
        print(f'power show:{comand}')
        # encoder
        comand = '#043' + str(config_data['encoder']) + '$'
        flag += self.send_command(comand)
        print(f'encoder:{comand}')
        # color
        comand = '#044' + str(config_data['color']) + '$'
        flag += self.send_command(comand)
        print(f'color:{comand}')
        # power save start
        comand = '#045' + str(config_data['power_save_start']) + '$'
        flag += self.send_command(comand)
        print(f'power save start:{comand}')
        # power save end
        comand = '#046' + str(config_data['power_save_end']) + '$'
        flag += self.send_command(comand)
        print(f'power save end:{comand}')
        # power deep save
        comand = '#047' + str(config_data['power_deep_save']) + '$'
        flag += self.send_command(comand)
        print(f'power deep save:{comand}')
        # finger pin
        comand = '#048' + str(config_data['finger_pin']) + '$'
        flag += self.send_command(comand)
        print(f'finger pin:{comand}')
        # x mode
        comand = '#049' + str(config_data['x_mode']) + '$'
        flag += self.send_command(comand)
        print(f'x mode:{comand}')
        # x input
        comand = '#04a' + str(config_data['x_input']) + '$'
        flag += self.send_command(comand)
        print(f'x input:{comand}')
        # update flag
        comand = '#04b' + str(config_data['update']) + '$'
        flag += self.send_command(comand)
        print(f'update flag:{comand}')
        # connect flag
        comand = '#04c' + str(config_data['connect']) + '$'
        flag += self.send_command(comand)
        print(f'connect flag:{comand}')
        # wifi ssid
        # comand = '#04d' + config_data['wifi_ssid'] + '$'
        # flag += self.send_command(comand)
        # print(f'wifi ssid:{comand}')
        # wifi password
        # comand = '#04e' + config_data['wifi_ps'] + '$'
        # flag += self.send_command(comand)
        # print(f'wifi password:{comand}')
        # print(f'flag:{flag}')

        # ble connect
        if connect_flag == '2':
            command = '#070$'
            response = self.get_ble_address(command)
            if 'BLE Address' in response:
                address = response.split('BLE Address:')[1].strip()
                print(f'ble address:{address}')
                self.add_ble_address(address)

        if flag >= 13:
            # 发送重启命令
            command = '#060$'
            self.send_command(command)
            return 1
        else:
            return 0
    
    

    def wire_update_weather(self):
         # wire connect
        try:
            weather_data = self.weather.get_weather_data()
            comand = '#080' + weather_data + '$'
            print(f'weather command:{comand}')
            self.ser.write(comand.encode())
            time.sleep(1)
            if self.ser.in_waiting:
                response = self.ser.read(self.ser.in_waiting).decode()
                print(f'weather response:{response}')
                if '$001#' in response:
                    self.connected = True
                    self.connect_flag = 0
                    return 1
                if '$000#' in response:
                    self.connect_flag = 0
                    return 0
        except:
            self.connect_flag = 0
            return -1

    def add_ble_address(self, address):
        config_path = 'gallery/app/view/ek3.config'
        if not os.path.exists(config_path):
            return 0
        config_dict = {}
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=')
                    config_dict[key] = value
                    
        config_dict['ble_address'] = address
        
        # 写回文件
        with open(config_path, 'w', encoding='utf-8') as f:
            for key, value in config_dict.items():
                f.write(f"{key}={value}\n")

if __name__ == '__main__':
    test = UartConnect()
    test.add_ble_address('AC:15:18:C0:D9:7A')
