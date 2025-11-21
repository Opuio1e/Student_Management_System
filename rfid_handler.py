import serial
ser = serial.Serial('COM3', 9600, timeout=1)  # adjust port and baudrate
tag_bytes = ser.readline()  # read a line (bytes ending with newline)
tag_id = tag_bytes.strip().decode('utf-8')  # e.g. "04A1B2C3"
