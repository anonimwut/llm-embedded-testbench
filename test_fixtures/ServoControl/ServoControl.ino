#include <Servo.h>

Servo myservo; // create a servo object

void setup() {
  myservo.attach(9); // attaches the servo on pin 9 to the servo object
  Serial.begin(9600); // start the serial communication with the speed of 9600 bps
}

void loop() {
  if (Serial.available()) {
    // Check if received string is "pos="
    if(Serial.find("pos=")) {
      int pos = Serial.parseInt(); // read the number that follows "pos="
      
      // map and constrain input to a suitable range
      pos = constrain(pos, 0, 180);
      
      // tell servo to go to position in variable 'pos'
      myservo.write(pos);
    }
  }
}
