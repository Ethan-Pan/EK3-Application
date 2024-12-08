import serial

ser = serial.Serial('COM3', 115200, timeout=1)
ser.write('#001$'.encode())
if ser.is_open:
    print('open')
else:
    print('close')