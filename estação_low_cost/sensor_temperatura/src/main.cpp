#include <Arduino.h>

#define LM35_PIN 36  // GPIO36 = ADC1_CH0

void setup() {
  Serial.begin(115200);
  analogReadResolution(12); // 12 bits → 0 a 4095
  pinMode(LM35_PIN, INPUT);
  Serial.println("Leitura do sensor LM35 iniciada...");
}

void loop() {
  int adc = analogRead(LM35_PIN);  // valor cru do ADC
  float tensao = adc * (3.3 / 4095.0);  // conversão para Volts (assumindo Vref = 3.3V)
  float temperaturaC = tensao / 0.01;  // LM35: 10mV por grau → 0.01V por °C

  // Impressão
  Serial.print("ADC: ");
  Serial.print(adc);
  Serial.print(" | Tensão: ");
  Serial.print(tensao, 3);
  Serial.print(" V | Temperatura: ");
  Serial.print(temperaturaC, 1);
  Serial.println(" °C");

  delay(1000);
}
