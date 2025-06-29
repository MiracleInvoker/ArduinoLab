import serial

ser = serial.Serial('COM5', 9600)

while True:
    data = int(ser.readline().decode())
    print(data)