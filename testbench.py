# Runs code compile end execution verification for a series of physical test setups. 
# Right now verification is not implemented, only generating, compiling, and uploading. 
# I've only tested it with PaLM so far becasue I don't have payment set up on a GPT account yet for API access. 

# Include your PaLM API key in a file called PaLM.key in the same directory as this file.
# Include your OpenAI API key in a file called OpenAI.key in the same directory as this file.
# Select Test Params:
service = 'OpenAI' #Select either Google or OpenAI or Text (for a folder of program files)
#model = 'models/text-bison-001' #Model to use for Google/OpenAI
model = "gpt-3.5-turbo"
temperature = 0.7 #Temperature for Google/OpenAI
repetitions = 50 #Number of times to repeat each llm_prompt
max_calls_per_minute = 30 # Max calls per minute for Google/OpenAI
port = '/dev/cu.usbmodem21101' #Port to upload to
servo_port = '/dev/cu.usbmodem21301' #Servo port
verify_port = '/dev/cu.usbmodem21201' #Port to verify on
arduino_type = 'arduino:avr:uno' #Type of Arduino
scratch_name = "prog" #Name of the scratch Arduino project
save_programs = True #Save the programs generated by the llm_prompts
baudrate = 9600 #Baudrate for serial communication. This should be specified in your prompts!

# Modes: 'check_string', 'IMU', '1D'
mode = 'IMU'
# String mode params
timeout = 5 #Timeout for serial communication in HW verification test
expected_msg = "Hello World!" #Expected message in HW verification test
# IMU/1D mode params
threshold = 500 #Threshold for correlation coefficient/tolerance in HW verification test. Update accordingly

import subprocess, os, re, json, time, serial, shutil
from datetime import datetime
import numpy as np
import comparison as comp
import imu_processing as imu

# Set up LLM Service
if service == 'Google':
    import google.generativeai as palm
    with open("PaLM.key", "r") as file:
        palm_key = file.read()
    palm.configure(api_key=palm_key) 

elif service == 'OpenAI':
    import openai
    with open("OpenAI.key", "r") as file:
        openai.api_key = file.read()
    MODEL = model


# Read in the llm_prompts
with open("llm_prompts.json", "r") as file:
    llm_prompts = json.load(file)
    llm_prompts = llm_prompts['llm_prompts']

# Functions to extract code segments and build code string
def extract_code_segments(content):
    # Regular expression to match code blocks
    pattern = r"```(.+?)```"

    # re.DOTALL makes '.' match newline characters as well
    code_blocks_raw = re.findall(pattern, content, re.DOTALL)

    # Remove language identifiers if present
    code_blocks = []
    for block in code_blocks_raw:
        # Splitting block into lines
        lines = block.split('\n')
        # Discard first line (assuming it's a language identifier)
        code_blocks.append('\n'.join(lines[1:]))

    return code_blocks

def build_code_string(code_segments):
    code_string = "\n\n".join(code_segments)
    return code_string

# Function to make folders/directories
def make_folder(path):
    if os.path.exists(path):
        # print("Folder already exists!")
        pass
    else:
        # Create a new folder
        os.mkdir(path)
        # print("Folder created successfully!")

# Initialize results storage
now = datetime.now()
dirname = now.strftime("%Y-%m-%d-%H-%M-%S")
# Check if the folder already exists
make_folder(dirname)

results = {}
for llm_prompt in llm_prompts:
    if save_programs:
        make_folder(dirname + '/' + llm_prompt['name'])
    results[llm_prompt['name']] = {"attempted": 0, "passed": 0, "compiled": 0}
with open("results.json", "w") as file:
    json.dump(results, file)

# Generate code for each llm_prompt
start_time = time.time()
calls = 0
for llm_prompt in llm_prompts:
    print("Starting test " + llm_prompt['name'] + ' ' + 'for ' + str(repetitions) + ' repetitions...')
    if save_programs:
        make_folder(dirname + '/' + llm_prompt['name'] + '/' + 'Pass')
        make_folder(dirname + '/' + llm_prompt['name'] + '/' + 'Fail')
    for ii in range(repetitions):
        # Generate code
        success = True # progress flag
        print('Starting test ' + str(ii+1) + ' of ' + str(repetitions))
        if service == 'Google':
            output = palm.generate_text(model=model, prompt=llm_prompt['text'], temperature=temperature, max_output_tokens=8000)
            result = output.result
        elif service == 'OpenAI':
            while True:
                try: # OpenAI is sometimes overloaded so you need to retry
                    response = openai.ChatCompletion.create(model=MODEL,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": llm_prompt['text']},
                        ],
                        temperature=temperature, 
                        timeout=60,
                    )
                    result = response['choices'][0]['message']['content']
                    break  # If the request was successful, break the loop
                except Exception as e:
                    print(f"An error occurred: {e}. Retrying in 5 seconds...")
                    time.sleep(5)
        # Try to extract the code, but sometimes LLM gives weird text so just use a dummy program if it fails
        try: 
            code_segments = extract_code_segments(result)
            program = build_code_string(code_segments)
        except:
            success = False
            msg = "Could not parse output"
            program = ';could not parse llm output' #something that will fail to compile just in case
        # Prevents exceeding the API call limit
        calls += 1
        if calls % max_calls_per_minute == 0:
            elapsed_time = time.time() - start_time
            sleep_time = max(60 - elapsed_time, 0)  # ensure sleep_time is not negative
            time.sleep(sleep_time)
            start_time = time.time()  # reset the start time for the next set of 30 calls

        # Create Arduino project for Arduino CLI to compile (will be continuously overwritten)
        make_folder(scratch_name)

        # Create a text file within the folder (overwriting if it already exists)
        with open(scratch_name + '/' + scratch_name + '.ino', "w") as file:
            # Write "Hello world" to the file
            file.write(program)
            # print("File created successfully!")
        #Attempt to build the Arduino project
        if success == True:
            command = ['arduino-cli', 'compile', '--fqbn', arduino_type, scratch_name]
            output = subprocess.run(command, capture_output=True, text=True)
            msg = ""
            if output.returncode != 0:
                success = False
                msg = "Compilation failed!"
                # print(output.stderr)
            else:
                results[llm_prompt["name"]]["compiled"] += 1
        # Attempt to upload the Arduino project

        if success == True:        
            command = ['arduino-cli', 'upload', '-p', port, '--fqbn', arduino_type, tmp]
            try:
                output = subprocess.run(command, capture_output=True, text=True, timeout=10)
                if output.returncode != 0:
                    success = False
                    msg = "Upload failed!"
            except subprocess.TimeoutExpired:
                success = False
                msg = "Upload timed out!"
        
        ## Implement HW Signal Verification here
        if success == True:
            if mode == 'check_string':
                start_time = time.time()
                ser = serial.Serial(port, baudrate)
                output_list = []
                while True:
                    if ser.in_waiting:
                        line = ser.readline().decode('utf-8').strip() 
                        if expected_msg in line:
                            success = True
                            break
                        else:
                            success = False
                            msg = "HW Signal Verification failed!"
                            break
                    if time.time() - start_time > timeout:
                        success = False
                        msg = "HW Signal Verification timed out!"
                        break
            elif mode == 'IMU':
                cmd1 = ['python', './serialtofile.py', port, str(baudrate), dirname + '/test_data.txt', str(timeout), str(1)]
                cmd2 = ['python', './serialtofile.py', verify_port, str(baudrate), dirname + '/verify_data.txt', str(timeout), str(1)]
                for pos in [0, 45, 90]: # servo angles
                    if success == True:
                        ser = serial.Serial(servo_port, baudrate)
                        time.sleep(2) # give the connection time to settle
                        command = f"pos={pos}\n"  # \n is required to indicate the end of an input
                        ser.write(command.encode())
                        time.sleep(2)  # allow some time for the servo to move to the position
                        ser.close()
                        time.sleep(1)
                        commands = [cmd1, cmd2] 
                        n = 2 #the number of parallel processes 
                        for j in range(max(int(len(commands)/n), 1)):
                            procs = [subprocess.Popen(i, shell=False) for i in commands[j*n: min((j+1)*n, len(commands))] ]
                            for p in procs:
                                p.wait()
                        test_data = imu.load_data(dirname + '/test_data.txt')
                        verify_data = imu.load_data(dirname + '/verify_data.txt')
                        if test_data.isnull().all().any():
                            success = False
                            msg = "No output!"
                        elif verify_data.isnull().all().any():
                            raise ValueError("Could not read data from verify port!")
                        else:
                            test_means = imu.compute_means(test_data)
                            verify_means = imu.compute_means(verify_data)
                            for kk in range(3):
                                if abs(test_means[kk] - verify_means[kk]) > threshold:
                                    success = False
                                    break
                if success == False:
                    msg = 'HW Signal Verification failed!'
                else:
                    msg = 'HW Signal Verification passed!'

            elif mode == '1D':
                cmd1 = ['python', './serialtofile.py', port, str(baudrate), dirname + '/test_data.txt', str(timeout), str(0)]
                cmd2 = ['python', './serialtofile.py', verify_port, str(baudrate), dirname + '/verify_data.txt', str(timeout), str(0)]
                commands = [cmd1, cmd2] 
                n = 2 #the number of parallel processes 
                for j in range(max(int(len(commands)/n), 1)):
                    procs = [subprocess.Popen(i, shell=False) for i in commands[j*n: min((j+1)*n, len(commands))] ]
                    for p in procs:
                        p.wait()

                # compare the data
                data_test = comp.load_data_1D(dirname + '/test_data.txt')
                data_verify = comp.load_data_1D(dirname + '/verify_data.txt')
                if not np.any(data_test):
                    success = False
                    msg = "No output!"
                elif not np.any(data_verify):
                    raise ValueError("Could not read data from verify port!")
                else:
                    distance = comp.euclidian_distance(data_test, data_verify)
                    if distance > threshold:
                        success = False
                        msg = 'HW Signal Verification failed! dist = ' + str(distance)
                    else:
                        msg = 'HW Signal Verification passed! dist = ' + str(distance)
    
        # Update results
        results[llm_prompt["name"]]["attempted"] += 1
        if success == True:
            results[llm_prompt["name"]]["passed"] += 1
            # Write program to folder
            if save_programs:
                shutil.copyfile(scratch_name + '/' +scratch_name + '.ino', dirname + '/' + llm_prompt['name'] + '/' + 'Pass' + '/' + llm_prompt['name'] + str(ii) + '.ino')
            msg = "Success!" + msg
        else:
            if save_programs:
                shutil.copyfile(scratch_name + '/' +scratch_name + '.ino', dirname + '/' + llm_prompt['name'] + '/' + 'Fail' + '/' + llm_prompt['name'] + str(ii) + '.ino')

        # Write results to file in case something crashes
        with open(dirname + '/' + "results.json", "w") as file:
            json.dump(results, file)
        
        # Print results
        print("Test " + str(ii + 1) + ": " + msg )
        # print(result)
        # print(program)
        
