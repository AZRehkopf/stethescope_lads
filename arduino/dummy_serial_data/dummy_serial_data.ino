#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

#define ECGPIN      33
#define MICPIN      34
#define LEDPIN      2

int ecgValue;
int micValue;

BluetoothSerial SerialBT;

void setup() {
  SerialBT.begin("ESP32test"); //Bluetooth device name

  pinMode (LEDPIN, OUTPUT);
  pinMode (ECGPIN, INPUT);
  pinMode (MICPIN, INPUT);
}

void loop() {
  ecgValue = analogRead(ECGPIN);
  SerialBT.write(ecgValue >> 8);
  SerialBT.write(ecgValue);

  micValue = analogRead(MICPIN);
  SerialBT.write(micValue >> 8);
  SerialBT.write(micValue);
  delay(0.5);
}
