#include <Servo.h>

#define LED_RED 4
#define LED_GREEN 0
#define BUTTON 5

Servo servo;  

unsigned long buttonTime = 0;
unsigned long previousButtonTime = 0;

void ICACHE_RAM_ATTR isr() {
 
}

void delayNonBlocking(unsigned long duration) {
  unsigned long start = millis();
  while (millis() - start < duration) {}
}

void setup() {
  servo.attach(D4);
  servo.write(0);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(BUTTON, INPUT);
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_GREEN, LOW);
}

void loop() {

  buttonTime = millis();

  if(digitalRead(BUTTON) == HIGH)
    if(buttonTime - previousButtonTime > 250) {
      int pos = 0;
      digitalWrite(LED_RED, LOW);
      digitalWrite(LED_GREEN, HIGH);

      for(pos; pos <= 180; pos += 5) 
        servo.write(pos);
      
      delay(5000);

      digitalWrite(LED_RED, HIGH);
      digitalWrite(LED_GREEN, LOW);

      for(pos = 180; pos >= 0; pos -= 3) 
        servo.write(pos);  
      
      previousButtonTime = buttonTime;
    }
}
