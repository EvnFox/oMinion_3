#include "LowPower.h"

//Be sure to write fuses as below:
//avrdude -c usbtiny -p atmega328p -U lfuse:w:0xe2:m -U hfuse:w:0xd9:m -U efuse:w:0xff:m

int WIFI_SIG = 3;
int Pi_on = 5;
int IO = 6;
int Sampling_LED = 7;
int STROBE = 9;


int RECOVER = 0;
int Extend_Sleep = 0;
int SAMPLES = 0;
int MAX_Sample_Num = 3000;


void setup(void)
{
  pinMode(WIFI_SIG, INPUT_PULLUP);
  pinMode(IO, INPUT_PULLUP);
  pinMode(Pi_on, OUTPUT); 
  pinMode(Sampling_LED, OUTPUT);
  pinMode(STROBE, OUTPUT);

  digitalWrite(Pi_on, LOW);
  digitalWrite(Sampling_LED, LOW);
  digitalWrite(STROBE, LOW);

  for(int i = 0; i < 3; i++){
    digitalWrite(Sampling_LED, HIGH);
    digitalWrite(STROBE, HIGH);
    delay(400);
    digitalWrite(Sampling_LED, LOW);
    digitalWrite(STROBE, LOW);
    delay(100);
  }
}

void Pi_Samp() {
  digitalWrite(Pi_on, HIGH);

  for (int i = 1; i <= 12; i++){
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF); //36 seconds of sleep; could be to allow the Pi to boot up.
  }

  int WIFI_Status = digitalRead(WIFI_SIG);
  int Mission_Status = digitalRead(IO);

  do {
    digitalWrite(Sampling_LED, HIGH);
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
    WIFI_Status = digitalRead(WIFI_SIG);
    Mission_Status = digitalRead(IO);
    if (Mission_Status == LOW){
      RECOVER = 1;
    }
  }
  while (WIFI_Status == HIGH);

  digitalWrite(Sampling_LED, LOW);

  for (int i = 1; i <= 5; i++){
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);//20 second of sleep; likely acounts for delay in Pi shutdown to close neatly 
  }

  digitalWrite(Pi_on, LOW);
}

void Pi_Samp_RECOVER() {

  digitalWrite(Pi_on, HIGH);

  for (int i = 1; i <= 12; i++){
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);//36 seconds of sleep; could be to allow the Pi to boot up.
  }

  int WIFI_Status = digitalRead(WIFI_SIG);
  int Mission_Status = digitalRead(IO);

  do {
    digitalWrite(Sampling_LED, HIGH);
     //strobe(); removing strobe while Pi is on during recovery mode so that the Minion is not flashing while trying to transmit to Iridium satellite. 
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
    WIFI_Status = digitalRead(WIFI_SIG);
    Mission_Status = digitalRead(IO);
    if (Mission_Status == LOW){
      Extend_Sleep = 0;  //Disabled for now
    }
  }
  while (WIFI_Status == HIGH);

  digitalWrite(Sampling_LED, LOW);

  for (int i = 1; i <= 5; i++){
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);//20 second of sleep; likely acounts for delay in Pi shutdown to close neatly 
  }

  digitalWrite(Pi_on, LOW);
}


void strobe() {
 //  digitalWrite(STROBE, HIGH);
//  delay(100);
//  digitalWrite(STROBE, LOW);
//  delay(400);
//
//  digitalWrite(STROBE, HIGH);
//  delay(250);
//  digitalWrite(STROBE, LOW);
//  delay(750);
//
//  digitalWrite(STROBE, HIGH);
//  delay(100);
//  digitalWrite(STROBE, LOW);
//  delay(400);

  digitalWrite(STROBE, HIGH);
  delay(100);
  digitalWrite(STROBE, LOW);
  delay(500);

  digitalWrite(STROBE, HIGH);
  delay(100);
  digitalWrite(STROBE, LOW);
  delay(1300);
//adjusting strobe to two flashes but conserving total time to two seconds so that the strobe cycle is still 8 seconds of sleep and 2 seconds of strobe 
}

void loop(void) 
{

  Pi_Samp();

  SAMPLES = SAMPLES + 1;

  if (RECOVER == 1 || SAMPLES > MAX_Sample_Num) {

    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
    RECOVER = 0;

    while(1) {
      Pi_Samp_RECOVER();

      //This is the recovery sleep cycle. Set for 60 cycles of 10 seconds (sleep for 8s strobe for 2s) for 10 minutes of total sleep
      for (int i = 1; i <= 60; i++){
        LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
        strobe();
      }

      if (Extend_Sleep == 1){
        //This is the extended sleep cycle. Set for 180 cycles of 10 seconds for 30 MORE minutes asleep
        //Not currently accessed by the code 
        for (int i = 1; i <= 180; i++){
          LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
          strobe();
        }
      }
    }
  }
  //This is the time lapse sleep cycle. Set for 15 cycles of 4 seconds of sleep for a 1 minute of total sleep between each time lapse sampling cycle. 
  //This loop is accessed when Mission_Status == HIGH 
  for (int i = 1; i <= 15; i++){
    LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  }

}
