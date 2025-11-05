// HOW TO MAKE AN ARDUINO OHM METER
//
// https://www.circuitbasics.com/arduino-ohm-meter/
//


int analogPin = 0;
int raw = 0;
int Vin = 5;
float Vout = 0;
float R1 = 10000;
float R2 = 0;
float buffer = 0;

void setup(){
Serial.begin(9600);
}

void loop(){
  raw = analogRead(analogPin);
  if(raw){
    buffer = raw * Vin;
    Vout = (buffer)/1024.0;
    buffer = (Vin/Vout) - 1;
    R2 = R1 * buffer;


    Serial.print("R1: ");
    Serial.print(R1/1000);
    Serial.print(" K   Volt: ");
    Serial.print(Vout);
    Serial.print("   R2: ");
    Serial.print(R2/1000);
    Serial.println(" K");
    
    delay(500);
  }
}
