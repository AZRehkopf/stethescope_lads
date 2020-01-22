#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

#define ECGPIN      33
#define MICPIN      34
#define LEDPIN      2

int ecgValue;
int micValue;
bool collectData = false;

BluetoothSerial SerialBT;

void collectAndTransmit() {
  //Write starting value so receiver knows it is synced
  SerialBT.write(0xFF);
  SerialBT.write(0xFF);

  //Collect data until receiver sends byte
  while (collectData) {
    ecgValue = analogRead(ECGPIN);
    SerialBT.write(ecgValue >> 8);
    SerialBT.write(ecgValue);
  
    micValue = analogRead(MICPIN);
    SerialBT.write(micValue >> 8);
    SerialBT.write(micValue);
    delay(0.5);

    if (SerialBT.available()) {
      SerialBT.read();
      collectData = false;
    }
  }
}

void setup() {
  //Bluetooth device name
  SerialBT.begin("ESP32test");

  //Pin configurations
  pinMode (LEDPIN, OUTPUT);
  pinMode (ECGPIN, INPUT);
  pinMode (MICPIN, INPUT);
}

void loop() {
  //Wait for byte from python before transmitting
  if (SerialBT.available()) {
    SerialBT.read();
    
    //Delay for python to get ready to receive
    delay(100);
    
    //Start collecting data
    collectData = true;
    collectAndTransmit();
  }
  delay(20);
}
