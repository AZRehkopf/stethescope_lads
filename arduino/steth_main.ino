#include "steth_const.h"

const int micPin = 34;
const int ecgPin = 33;
const int ledPin = 2;
const word cfg = 0x00FF; // Indicator byte for ordering

word micValue = 0;
word ecgValue = 0;
int sendCount = 0;

hw_timer_t * timer = NULL;

bool smpFlag = false;

BluetoothSerial SerialBT;

void IRAM_ATTR smpTimer() {
  smpFlag = true;
}

void formPacket(word smp1, word smp2, word cfg) {
  // --- Note ---
  // Must send a configuration byte every x samples to help rx sync (tell which bytes are which)


  unsigned long pkt = 0; 

  //since cfg is reserveed, change any samples with that value
  if ((smp1 & cfg) == 0x00FF) {
    smp1 = smp1 - 1;
  }
  if ((smp2 & cfg) == 0x00FF) {
    smp2 = smp2 - 1;
  }
  
  pkt += smp1;
  pkt += (smp2 << 16);
  
  sendPacket(pkt);
}

void sendPacket(unsigned long pkt) {
  // Send 32 bit packet, 1 byte at a time
  SerialBT.write((pkt >> 24)); // First byte
  SerialBT.write((pkt >> 16));
  SerialBT.write((pkt >> 8));
  SerialBT.write(pkt);
}

void sendCfg(word cfg) {
  SerialBT.write(cfg);
}

void setup() {
  SerialBT.begin("ESP32test");

  pinMode (ledPin, OUTPUT);
  pinMode (micPin, INPUT);
  pinMode (ecgPin, INPUT);

  // div down internal 80MHz clock
  timer = timerBegin(0, 80, true);
  // Attach onTimer function to our timer.
  timerAttachInterrupt(timer, &smpTimer, true);

  // Set alarm to call onTimer function every second (value in microseconds).
  // Repeat the alarm (third parameter)
  timerAlarmWrite(timer, SAMP_MS, true);

  // Start an alarm
  timerAlarmEnable(timer);
}

void loop() {
  if (SerialBT.available()) {
    if (smpFlag) {
      // 12 bit samples
      micValue = (0x0FFF & analogRead(micPin));
      ecgValue = (0x0FFF & analogRead(ecgPin));
      //micValue = (0x0FFF & 1);
      //ecgValue = (0x0FFF & 2);
      smpFlag = false;
      sendCount = sendCount + 1;
      formPacket(micValue, ecgValue, cfg);
    }
    if (sendCount == CFG_CNT) {
      sendCfg(cfg);
      sendCount = 0;
    }
  }
}
