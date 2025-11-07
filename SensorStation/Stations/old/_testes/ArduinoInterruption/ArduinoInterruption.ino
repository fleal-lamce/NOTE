const byte ledPin = 13;
const byte interruptPin = 2;
volatile byte state = LOW;
int count=0;

void setup() {
  Serial.begin(9600);          //inicia serial em 9600 baud rate
  Serial.println("-------------------------------");

  pinMode(ledPin, OUTPUT);
  pinMode(interruptPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(interruptPin), blink, CHANGE);
}

void loop() {
  digitalWrite(ledPin, state);
}

void blink() {
  state = !state;
  Serial.println(count);
  count++;
}
