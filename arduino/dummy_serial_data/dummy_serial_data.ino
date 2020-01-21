//This example code is in the Public Domain (or CC0 licensed, at your option.)
//By Evandro Copercini - 2018
//
//This example creates a bridge between Serial and Classical Bluetooth (SPP)
//and also demonstrate that SerialBT have the same functionalities of a normal Serial

#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;
unsigned long randvoltage;

void setup() {
  SerialBT.begin("ESP32test"); //Bluetooth device name
  randomSeed(analogRead(0));
}

void loop() {
  for (int i = 0; i < 256; i++) {
    SerialBT.write(i);
    delay(0.05);
  }
}
