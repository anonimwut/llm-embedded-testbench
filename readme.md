# LLM Embedded System Testbench
This is an anonymized repo containing code for a testbench for programatically generating and testing embedded system code - once moved to a non-anonymous repo, we will update this readme to include additional information. 

## Overview
This program works by generating a program using a LLM api, then compiles and uploads the program to a microcontroller. The microcontroller then runs the code, and the serial outputs from the test microcontroller and a reference system using human-written code are compared to verify the correct behavior of the generated code. 

## Getting Started
### Prerequisites
This project contains an ``environment.yml`` file which you can use to replicate the environment used to run this project. However, as the LLM api packages are updated very frequently, I recommend installing those first, then installing packages as-needed to run the remainder of the code to ensure you don't get stuck with issues solving the environment. 
### Supported LLM Packages
This project supports LLMs from Google and OpenAI using the following packages. Syntax has changed slightly with recent versions so use these versions for now:
- Google (PaLM models): ``google-generativeai v0.2.2``
- OpenAI (GPT-3.5, GPT-4, etc.): ``openai v0.28.1``
### Hardware Setup
This project supports all boards supported by the Arduino IDE using the Arduino CLI interface. To use this, you must have the Arduino CLI installed and configured. See [here](https://arduino.github.io/arduino-cli/latest/installation/) for instructions on how to install and configure the Arduino CLI.
The CLI will interface with the same system configuration info as the Arduino IDE, so if you have a board or some libraries set up in the Arduino IDE, they should also be available to the CLI.

## Running Your First Test
To run your first test, first edit the ``llm_prompts.json`` file to include the prompt you want to test. The format of this file is as follows, note that you can choose to specify any number of prompts in the file, which could be useful if you want to compare the performance of different prompting strategies for a task. The example below includes two different prompt examples:
```
{
    "llm_prompts": [
        {
            "name": "test_name",
            "text": "write me an Arduino uno program for the Arduino Uno that prints "Hello World!\n" over serial every second at baud rate 9600."
        },
        {
            "name": "LSM6DSO",
            "text": "write me an Arduino uno program for the lsm6dso i2c IMU. It is connected to the default I2C pins on the arduino uno. Print the sensor output over Serial at baud rate 9600 every 100 millisecons. Here is an example output of a properly functioning program: _X = -0.517\nA_Y = 0.386\nA_Z = -0.749\nA_X = -0.517\nA_Y = 0.386\nA_Z = -0.749\nA_X = -0.517\n"
        }
    ]
}
```
Next, open the ``testbench.py`` file and adjust the script parameters at the top of the file to match your setup. The parameters are as follows:
- __service__: the LLM API to use. Currently supported options are ``Google`` and ``OpenAI``. 
- __model__: the specific model to use. This includes ``models/text-bison-001`` for Google and models like ``gpt-3.5-turbo`` and ``gpt-4`` for OpenAI. 
-__temperature__: the temperature to use for the LLM. 
- __repetition__: the number of times to try each prompt
- __max_calls_per_minute__: the maximum number of calls to the LLM API to make per minute. This is useful to avoid hitting the API rate limit for models that have a limit expressed in requests per minute. Most APIs have now moved on to tokens/min for limits. 
- __port__: the port on the computer that the Arduino to run LLM code is connected to. You can find this port by opening Arduino IDE and seeing which port the different boards are connected to. It might look something like ``COM3`` or ``/dev/cu.usbmodem14101`` depending on your operating system.
- __servo_port__: the port on the computer that is controlling the servo, currently used for IMU tests
- __verify_port__: the port on the computer that the Arduino to run human-written code is connected to. This is used to verify the output of the LLM code.
- __arduino_type__: the type of Arduino connected to ``port``. This is used to determine the correct board type to use when calling the build and upload commands in the Arduino CLI
- __scratch_name__: the name of the scratch file to use to store the LLM generated code before it is compiled and uploaded to the Arduino. You should only change this if for some reason Arduino CLI is having issues accessing the file in the project directory. 
- __save_programs__: whether or not to save each generated program to the ``programs`` directory. This is useful for debugging and for generating a dataset of programs for future use.
- __baudrate__: the baudrate to use for the serial connection to the Arduino. This should match the baudrate specified in your LLM prompts as well!
- __mode__: the type of test to run. Currently supports 3 tests - ``check_string``, ``1D``, and ``IMU``.
- __timeout__: the timeout for how long to listen for serial output from the connected Arduino boards. For most tests, something between 5-10s should be sufficient. 
- __expected_msg__: for the ``check_string`` test, this is the string to expect from the Arduino running human-written code. 
- __threshold__: for the ``1D`` test, this is the threshold for the maximum euclidean distabce between the LLM and human-written code outputs. For the ``IMU`` test, this is the threshold for the allowable difference in average values for each position and each IMU axis. To find the appropriate threshold, test with human-written code first to understand the expected range of values for correct code. 

### API keys:
You will need either a Google or OpenAI API key to run this code. You can place the key for each vendor in a file called ``OpenAI.key`` or ``PaLM.key`` in the root directory of the project. The code will automatically read the key from the file and use it to authenticate with the API.

## Adding your own tests: 
For test fixtures where serial output is simply a 1D array, you may be able to use the already-implemented ``1D`` test. For tests where a single string must be verified, the ``check_string`` test may be useful. For more complex tests, you will need to implement it yourself. For example, the ``IMU`` test includes activating a servo after uploading the code to the Ardunino and reading serial output at several different positions. To implement your own test, you will need to add an additional upload sequence to ``testbench.py`` and perhaps add new functions in a separate file to process the data from the Arduino(s) and verify the output. 
