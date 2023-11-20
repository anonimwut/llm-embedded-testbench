from Phidget22.Phidget import *
from Phidget22.Devices.Stepper import *
import time

def main():
        stepper0 = Stepper()
        stepper0.openWaitForAttachment(5000)
        try:
            while True:
                stepper0.setTargetPosition(-1000000)
                stepper0.setEngaged(True)
                stepper0.setCurrentLimit(1.5)
                stepper0.setAcceleration(100000)
                stepper0.setVelocityLimit(100000)

                time.sleep(10)
                
                stepper0.setTargetPosition(200000)
                stepper0.setEngaged(True)

                time.sleep(10)
            
        except (Exception, KeyboardInterrupt):
            #Ctrl-C to stop
            pass
        stepper0.close()

main()
