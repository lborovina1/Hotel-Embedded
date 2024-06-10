#include <Servo.h>
#include "EspMQTTClient.h"

#define LED_RED D2
#define LED_GREEN D1
#define SERVO D4

Servo servo;

EspMQTTClient client(
  "Asterix_WLAN",       // WiFi SSID
  "123A456d78",         // WiFi Password
  "broker.hivemq.com",  // MQTT Broker server ip
  "TestClient",         // Klijentsko ime, identifikator uredjaja 
  1883                  // MQTT port, default-ni 1883
);

// Ova funkcija se poziva kada je konekcija uspostavljena (Wifi i MQTT)
void onConnectionEstablished() {
  LEDSignal();
  Serial.println("WiFi Connected");
  client.publish("USprojekat/Konekcija", "Device Online", true);
  client.publish("USprojekat/ZelenoSvjetlo", "0");
  client.publish("USprojekat/CrvenoSvjetlo", "1");
  client.publish("USprojekat/Servo", "0");
  
  // Subscribe na temu "USprojekat/Servo" 
  client.subscribe("USprojekat/Servo", 
    [](const String & payload) {
      Serial.println(payload);

      if(payload == "1") {
        // Pali se zelena LED za signalizaciju dizanja rampe 
        client.publish("USprojekat/ZelenoSvjetlo", "1");
        client.publish("USprojekat/CrvenoSvjetlo", "0");
        digitalWrite(LED_RED, LOW);
        digitalWrite(LED_GREEN, HIGH);

        // Rampa se dize
        Serial.println("Podizem rampu...");
        client.publish("USprojekat/Info", "Podizem rampu...");
        int pos = 0;
        for(pos; pos <= 180; pos += 5) // Rampa se postepeno dize, povecanjem ugla otklona
          servo.write(pos);

        // Cekanje 10 sekundi da automobil prodje 
        Serial.println("Rampa podignuta!");
        client.publish("USprojekat/Info", "Rampa podignuta!");
        delay(10000);

        // Pali se crvena LED za signalizaciju spustanja rampe
        client.publish("USprojekat/ZelenoSvjetlo", "0");
        client.publish("USprojekat/CrvenoSvjetlo", "1");
        digitalWrite(LED_RED, HIGH);
        digitalWrite(LED_GREEN, LOW);

        // Rampa se spusta
        Serial.println("Spustam rampu...");
        client.publish("USprojekat/Info", "Spustam rampu...");
        for(pos = 180; pos >= 0; pos -= 3)  // Rampa se postepeno spusta, smanjenjem ugla otklona
          servo.write(pos); 
        
        Serial.println("Rampa spustena.");
        client.publish("USprojekat/Info", "Rampa spustena.");
        client.publish("USprojekat/Servo", "0");    
      }
    });
}

// Funkcija koja se koristi kao signalizator uspostavljene konekcije (blicanje ugradjene LED)
void LEDSignal() {
  digitalWrite(LED_BUILTIN, HIGH);  
  delay(100);                      
  digitalWrite(LED_BUILTIN, LOW);   
  delay(100);   
  digitalWrite(LED_BUILTIN, HIGH);  
  delay(100);                      
  digitalWrite(LED_BUILTIN, LOW);   
  delay(100);   
  digitalWrite(LED_BUILTIN, HIGH);  
  delay(100);                      
  digitalWrite(LED_BUILTIN, LOW);   
  delay(100);   
}

void setup() {
  Serial.begin(115200);
  
  client.enableLastWillMessage("USprojekat/Konekcija", "Device Offline", true);  
  client.enableMQTTPersistence();

  servo.attach(SERVO);            // Povezivanje motora sa mikrokontrolerom preko macro-a SERVO
  servo.write(0);                 // Postavljanje inicijalne pozicije rampe
  pinMode(LED_RED, OUTPUT);       // Inicijalizacija crvene LED 
  pinMode(LED_GREEN, OUTPUT);     // Inicijalizacija zelene LED

  // Na pocetku crvena LED upaljena, a zelena ugasena zato sto je rampa spustena
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_GREEN, LOW);
}

void loop() {
  // Provjerava se prijem nove poruke svakih 250ms
  client.loop();
  delay(250);
}
