import requests
import subprocess
import os
import certifi
import re


class Ota:
    def __init__(self):
        self.ota_url = 'https://jmlstudio.cn/ota/'
        self.ota_save_path = os.path.join(os.path.expanduser('~'), '.ek3')
        self.latest_version = None

    # EK3-firmware or EK-Home-release
    def check_version(self, version_type):
        # 禁用代理
        proxies = {
            'http': None,
            'https': None 
        }
        
        try:
            # 使用 certifi 提供的证书
            response = requests.get(self.ota_url, 
                                proxies=proxies, 
                                timeout=30,
                                verify=certifi.where())  # 使用证书验证
            
            if response.status_code == 200:
                content = response.text
                version_match = re.search(version_type + r'-(\d+\.\d+)', content)
                if version_match:
                    version = version_match.group(1)
                    print(f"发现固件,版本号:{version}")
                    self.latest_version = version
                    return version
                else:
                    print("未发现新固件")
                    return False
            else:
                print(f"检查更新失败，状态码：{response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"网络请求出错：{str(e)}")
            return False


    def downLoad(self):  
        if self.latest_version:
            firmware_name = 'EK3-firmware-' + self.latest_version + '.bin'
            url = self.ota_url + firmware_name
            # 禁用代理
            proxies = {
                'http': None,
                'https': None
            }
            
            try:
                # 使用 certifi 提供的证书
                response = requests.get(url, 
                                    proxies=proxies, 
                                timeout=30,
                                    verify=certifi.where())  # 使用证书验证

                if response.status_code == 200:
                    with open(self.ota_save_path + '/' + firmware_name, 'wb') as f:
                        f.write(response.content)
                        print("固件下载成功")
                        return True
                else:
                    print(f"固件下载失败，状态码：{response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"下载出错：{str(e)}")
            return False

    def flash_firmware(self, port):
        if self.latest_version:
            firmware_name = 'EK3-firmware-' + self.latest_version + '.bin'
            try:
                import ctypes
                import sys
                
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

                kernel32.AllocConsole()
                
                # 保存原始的标准输入输出
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                
                # 创建新的输出流
                stdout = open('CONOUT$', 'w')
                stderr = open('CONOUT$', 'w')
                
                sys.stdout = stdout
                sys.stderr = stderr
                
                print("开始固件更新，请勿断开设备...")
                
                import esptool
                command = [
                    '--chip', 'esp32',
                    '--port', port,
                    '--baud', '921600',
                    'write_flash', '0x10000',
                    self.ota_save_path + '/' + firmware_name
                ]
                
                try:
                    esptool.main(command)
                    print("\n固件更新成功！")
                    success = True
                except Exception as e:
                    print(f"\n固件更新失败：{str(e)}")
                    success = False
                    raise e
                finally:
                    # 恢复原始的标准输出
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                    
                    # 关闭输出流
                    stdout.close()
                    stderr.close()
                    
                    # 释放控制台
                    kernel32.FreeConsole()
                
                return success
                
            except Exception as e:
                print(f"烧录错误: {str(e)}")
                return False

# 使用示例
if __name__ == '__main__':
    ota = Ota()
    # ota.check_version('EK3-firmware')
    # ota.downLoad()
    ota.latest_version = '1.2'
    ota.flash_firmware('COM3')
