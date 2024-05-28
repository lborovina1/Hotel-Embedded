#include <Servo.h>
#include "EspMQTTClient.h"

#define LED_RED D2
#define LED_GREEN D1
#define BUTTON D5

Servo servo;

EspMQTTClient client(
  "Asterix_WLAN",       // WiFi SSID
  "123A456d78",         // WiFi Password
  "broker.hivemq.com",  // MQTT Broker server ip
  "TestClient",         // Client name that uniquely identify your device
  1883                  // The MQTT port, default to 1883. this line can be omitted
);

// This function is called once everything is connected (Wifi and MQTT)
void onConnectionEstablished() {
  client.publish("USprojekat/Konekcija", "Device Online", true);
  client.publish("USprojekat/ZelenoSvjetlo", "0");
  client.publish("USprojekat/CrvenoSvjetlo", "1");
  
  // Subscribe to "USprojekat/Servo" to work with all the functionalities
  client.subscribe("USprojekat/Servo", 
    [](const String & payload) {
      Serial.println(payload);

      if(payload == "1") {
        // Set LEDs to GO
        client.publish("USprojekat/ZelenoSvjetlo", "1");
        client.publish("USprojekat/CrvenoSvjetlo", "0");
        digitalWrite(LED_RED, LOW);
        digitalWrite(LED_GREEN, HIGH);

        // Raise the ramp
        Serial.println("Podizem rampu...");
        client.publish("USprojekat/Info", "Podizem rampu...");
        int pos = 0;
        for(pos; pos <= 180; pos += 3) 
          servo.write(pos);

        // Wait 5s for the car to pass
        Serial.println("Rampa podignuta!");
        client.publish("USprojekat/Info", "Rampa podignuta!");
        delay(5000);

        // Set LEDs to GO
        client.publish("USprojekat/ZelenoSvjetlo", "0");
        client.publish("USprojekat/CrvenoSvjetlo", "1");
        digitalWrite(LED_RED, HIGH);
        digitalWrite(LED_GREEN, LOW);

        // Lower the ramp
        Serial.println("Spustam rampu...");
        client.publish("USprojekat/Info", "Spustam rampu...");
        for(pos = 180; pos >= 0; pos -= 2) 
          servo.write(pos); 
        
        Serial.println("Rampa spustena.");
        client.publish("USprojekat/Info", "Rampa spustena.");
        client.publish("USprojekat/Servo", "0");    
      }
    });
}

void setup() {
  Serial.begin(115200);

  client.enableLastWillMessage("USprojekat/Konekcija", "Device Offline", true);  

  servo.attach(D4);               // Set the pin for the servo
  servo.write(0);                 // Set the servo to 0 position
  pinMode(LED_RED, OUTPUT);       // Set the pin for STOP LED
  pinMode(LED_GREEN, OUTPUT);     // Set the pin for GO LED

  // Set LEDs to STOP position on start
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_GREEN, LOW);
}

void loop() {
  // Scan for new messages every 250ms
  client.loop();
  delay(250);
}
