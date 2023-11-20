import sys
import serial
import time

port = sys.argv[1]
baudrate = int(sys.argv[2])
file_name = sys.argv[3]
timeout = int(sys.argv[4])
imu = int(sys.argv[5])

start_time = time.time()
ser = serial.Serial(port, baudrate, timeout=1)

# Allow Arduino some time to start sending data
time.sleep(2) 
output_list = []
if imu==1:
    try:
        line = ''
        temp_list = []
        valid_lines_order = ['A_X', 'A_Y', 'A_Z']
        index = 0

        while time.time() - start_time < timeout:  # read until timeout seconds
            if ser.in_waiting:
                c = ser.read().decode('utf-8', errors='ignore')  # read a byte
                if c == '\n':  # if the byte is a newline character
                    if line.startswith('A_') and line.count('=') == 1:  # if the line is valid
                        line_prefix = line.split(' ')[0]
                        if line_prefix == valid_lines_order[index]:
                            temp_list.append(line.strip() + "\n")
                            index += 1
                        else:
                            # Reset the temporary list and index
                            temp_list = []
                            index = 0

                        # If the group is complete, append to output_list
                        if index == len(valid_lines_order):
                            output_list.extend(temp_list)
                            temp_list = []
                            index = 0

                    line = ''  # reset the line
                else:
                    line += c  # add the byte to the line
        ser.close()
    except Exception as e:
        print(f"An error occurred: {e}")
        ser.close()

    with open(file_name, "w") as file:
        file.writelines(output_list)
    
else:
    output_list = []
try:
    line = ''
    while time.time() - start_time < timeout:  # read until timeout seconds
        if ser.in_waiting:
            c = ser.read().decode('utf-8', errors='ignore')  # read a byte
            if c == '\n':  # if the byte is a newline character
                output_list.append(line.strip() + "\n")
                line = ''  # reset the line
            else:
                line += c  # add the byte to the line
    ser.close()
except Exception as e:
    print(f"An error occurred: {e}")
    ser.close()

with open(file_name, "w") as file:
    file.writelines(output_list)
