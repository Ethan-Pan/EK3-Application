import requests
from datetime import datetime

# https://api.seniverse.com/v3/weather/now.json?key=SopS99tRo91DaoxpD&location=shenzhen&language=zh-Hans&unit=c
class WeatherAPI:
    def __init__(self, city_id):
        self.api_key = 'SopS99tRo91DaoxpD'   # 心知天气 API KEY one year valid from 2024-11-29
        self.city_id = city_id
        self.feels_like = None
        self.humidity = None
        self.weather_code = None
        self.high_temp = None
        self.low_temp = None
        self.month = None
        self.day = None
        self.weekday = None
        self.hour = None
        self.minute = None
        self.second = None
        self.url_now = f'https://api.seniverse.com/v3/weather/now.json?key={self.api_key}&location={self.city_id}&language=zh-Hans&unit=c'
        self.url_daily = f'https://api.seniverse.com/v3/weather/daily.json?key={self.api_key}&location={self.city_id}&language=zh-Hans&unit=c&start=0&days=5'
        # 禁止代理访问
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.proxies = {
            'http': None,
            'https': None
        }

    def get_weather(self):
        try:
            response = requests.get(self.url_now, headers=self.headers, proxies=self.proxies, verify=True)
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                weather_data = data['results'][0].get('now', {})
                self.feels_like = weather_data.get('feels_like', '未知')
                self.humidity = weather_data.get('humidity', '未知')
                self.weather_code = weather_data.get('code', '未知')
                return 0
            else:
                print("未能获取到天气数据")
                return -1
        except ValueError as e:
            print(f"解析JSON数据失败: {e}")
            return None
        except Exception as e:
            print(f"获取天气数据时发生错误: {e}")
            return None
    
    def get_weather_daily(self):
        try:
            response_daily = requests.get(self.url_daily, headers=self.headers, proxies=self.proxies, verify=True)
            data_daily = response_daily.json()
            if 'results' in data_daily and len(data_daily['results']) > 0:
                daily_data = data_daily['results'][0]['daily'][0]
                self.high_temp = daily_data.get('high', '未知')
                self.low_temp = daily_data.get('low', '未知')
                return 0

        except ValueError as e:
            print(f"解析JSON数据失败: {e}")
            return None
        except Exception as e:
            print(f"获取天气数据时发生错误: {e}")
            return None 
        
    def get_time(self):
        try:
            # 获取当前时间并转换为中国时区
            current_time = datetime.now()
            
            # 格式化输出时间
            self.month = current_time.month
            self.day = current_time.day
            self.weekday = current_time.weekday()+1
            self.hour = current_time.hour
            self.minute = current_time.minute
            self.second = current_time.second
            return 0
        except Exception as e:
            print(f"获取时间时发生错误: {e}")
            return None
        
    def get_weather_data(self):
        self.get_weather()
        self.get_weather_daily()
        self.get_time()
        message = f"#{self.feels_like}#{self.humidity}#{self.weather_code}#{self.high_temp}#{self.low_temp}#{self.month}#{self.day}#{self.weekday}#{self.hour}#{self.minute}#{self.second}"
        print(f'weather data:{message}')
        return message


# 使用示例
if __name__ == "__main__":
    CITY_ID = 'shenzhen'
    weather_api = WeatherAPI( CITY_ID)
    weather_api.get_weather()
    weather_api.get_weather_daily()
    weather_api.get_time()
