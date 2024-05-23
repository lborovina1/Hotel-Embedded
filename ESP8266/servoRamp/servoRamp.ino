#include <Servo.h>

#define LED_RED D4
#define LED_GREEN D0
#define BUTTON D5

Servo servo;
unsigned long buttonTime = 0;
unsigned long previousButtonTime = 0;

void setup() {
  servo.attach(D4);               //Set the pin for the servo
  servo.write(0);                 //Set the servo to 0 position
  pinMode(LED_RED, OUTPUT);       
  pinMode(LED_GREEN, OUTPUT);
  pinMode(BUTTON, INPUT);
  digitalWrite(LED_RED, HIGH);    //Set LEDs to STOP
  digitalWrite(LED_GREEN, LOW);
}

void loop() {
  buttonTime = millis();

  if(digitalRead(BUTTON) == HIGH)
    //Debounce the button
    if(buttonTime - previousButtonTime > 250) {
      int pos = 0;
      //Switch the LEDs from STOP to GO
      digitalWrite(LED_RED, LOW);
      digitalWrite(LED_GREEN, HIGH);

      //Raise the ramp
      for(pos; pos <= 180; pos += 5) 
        servo.write(pos);
      //Wait for car to pass
      delay(5000);
      //Switch LEDs back from GO to STOP
      digitalWrite(LED_RED, HIGH);
      digitalWrite(LED_GREEN, LOW);

      //Lower the ramp
      for(pos = 180; pos >= 0; pos -= 3) 
        servo.write(pos);  
      
      //Update debouncing time
      previousButtonTime = buttonTime;
    }
}
