#include <Servo.h>
#include "EspMQTTClient.h"

#define LED_RED D2
#define LED_GREEN D1
#define BUTTON D5


Servo servo;

EspMQTTClient client(
  "Asterix_WLAN",
  "123A456d78",
  "broker.hivemq.com",  // MQTT Broker server ip
  "TestClient",     // Client name that uniquely identify your device
  1883              // The MQTT port, default to 1883. this line can be omitted
);

// This function is called once everything is connected (Wifi and MQTT)
// WARNING : YOU MUST IMPLEMENT IT IF YOU USE EspMQTTClient
void onConnectionEstablished()
{
  client.publish("USprojekat/Konekcija", "Device Online.", true);
  client.publish("USprojekat/ZelenoSvjetlo", "0");
  client.publish("USprojekat/CrvenoSvjetlo", "1");
  


  // Subscribe to "mytopic/test" and display received message to Serial
  client.subscribe("USprojekat/Servo", [](const String & payload) {
    Serial.println(payload);

    if(payload == "1") {
      Serial.println("Podizem rampu...");
      client.publish("USprojekat/Info", "Podizem rampu...", true);
      client.publish("USprojekat/ZelenoSvjetlo", "1");
      client.publish("USprojekat/CrvenoSvjetlo", "0");
      digitalWrite(LED_RED, LOW);
      digitalWrite(LED_GREEN, HIGH);
      int pos = 0;
      for(pos; pos <= 180; pos += 3) 
        servo.write(pos);
      //Wait for car to pass
      Serial.println("Rampa podignuta!");
      client.publish("USprojekat/Info", "Rampa podignuta!", true);
      delay(5000);
      //Switch LEDs back from GO to STOP
      client.publish("USprojekat/ZelenoSvjetlo", "0");
      client.publish("USprojekat/CrvenoSvjetlo", "1");
      digitalWrite(LED_RED, HIGH);
      digitalWrite(LED_GREEN, LOW);
      //Lower the ramp
      Serial.println("Spustam rampu...");
      client.publish("USprojekat/Info", "Spustam rampu...", true);
      for(pos = 180; pos >= 0; pos -= 2) 
        servo.write(pos); 
      
      Serial.println("Rampa spustena.");
      client.publish("USprojekat/Info", "Rampa spustena.", true);
      client.publish("USprojekat/Servo", "0");    
    }
  });

  /*
  // Subscribe to "mytopic/wildcardtest/#" and display received message to Serial
  client.subscribe("USprojekat/wildcardtest/#", [](const String & topic, const String & payload) {
    Serial.println("(From wildcard) topic: " + topic + ", payload: " + payload);
  });

  // Publish a message to "mytopic/test"
  client.publish("USprojekat/test", "This is a message"); // You can activate the retain flag by setting the third parameter to true

  // Execute delayed instructions
  client.executeDelayed(5 * 1000, []() {
    client.publish("USprojekat/wildcardtest/test123", "This is a message sent 5 seconds later");
  });
  */
}

void setup() {

  Serial.begin(115200);

  // Optional functionalities of EspMQTTClient
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
  client.enableHTTPWebUpdater(); // Enable the web updater. User and password default to values of MQTTUsername and MQTTPassword. These can be overridded with enableHTTPWebUpdater("user", "password").
  client.enableOTA(); // Enable OTA (Over The Air) updates. Password defaults to MQTTPassword. Port is the default OTA port. Can be overridden with enableOTA("password", port).
  client.enableLastWillMessage("TestClient/lastwill", "I am going offline");  // You can activate the retain flag by setting the third parameter to true


  servo.attach(D4);               //Set the pin for the servo
  servo.write(0);                 //Set the servo to 0 position
  pinMode(LED_RED, OUTPUT);       
  pinMode(LED_GREEN, OUTPUT);
  pinMode(BUTTON, INPUT);
  digitalWrite(LED_RED, HIGH);    //Set LEDs to STOP
  digitalWrite(LED_GREEN, LOW);
}

void loop() {
  client.loop();
  delay(100);
  /*

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
    


    //////////////////////////////////////////////////////////
    digitalWrite(LED_RED, LOW);
    digitalWrite(LED_GREEN, HIGH);
    int pos = 0;
    for(pos; pos <= 180; pos += 5) 
        servo.write(pos);
      //Wait for car to pass
      delay(2000);
      //Switch LEDs back from GO to STOP
      

      //Lower the ramp
      for(pos = 180; pos >= 0; pos -= 3) 
        servo.write(pos); 
      digitalWrite(LED_RED, HIGH);
      digitalWrite(LED_GREEN, LOW);

      delay(2000);
      //////////////////////////////////////////////////////////

      */


}
