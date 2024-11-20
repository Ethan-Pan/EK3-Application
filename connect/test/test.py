import matplotlib.pyplot as plt

def read_file(file, file2):
    f = open(file, mode='r')
    dataLines = f.readlines()
    voltage, charge = [], []
    for data in dataLines:
        voltage.append(int(data.split(':')[1].split(',')[0]))
        charge.append(int(data.split(':')[-1]))

    f2 = open(file2, mode='r')
    dataLines2 = f2.readlines()
    voltage2, charge2 = [], []
    for data in dataLines2:
        voltage2.append(int(data.split(':')[1].split(',')[0]))
        charge2.append(int(data.split(':')[-1]))
    
    plt.plot(list(range(len(voltage))), voltage)
    plt.plot(list(range(len(charge))), charge)
    plt.plot(list(range(len(voltage2))), voltage2)
    plt.plot(list(range(len(charge2))), charge2)
    plt.show()

file = r'C:\Users\12609\Documents\Cursor project\Python\EK3\ek3\connect\test\charge.txt'
file2 = r'C:\Users\12609\Documents\Cursor project\Python\EK3\ek3\connect\test\discharge.txt'

read_file(file, file2)
