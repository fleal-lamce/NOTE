#include <Arduino.h>

#define UV_SENSOR_PIN 36  // GPIO36 = ADC0_CH0

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  pinMode(UV_SENSOR_PIN, INPUT);
  Serial.println("Iniciado com sensor UV.");
}

float lerTensao() {
  int adc = analogRead(UV_SENSOR_PIN);
  return adc * (3.3 / 4095.0);
}

int calcularUVIndex(float tensao_mV) {
  int mV = tensao_mV * 1000;

  if (mV < 50) return 0;
  else if (mV < 227) return 1;
  else if (mV < 318) return 2;
  else if (mV < 408) return 3;
  else if (mV < 503) return 4;
  else if (mV < 606) return 5;
  else if (mV < 696) return 6;
  else if (mV < 795) return 7;
  else if (mV < 881) return 8;
  else if (mV < 976) return 9;
  else if (mV < 1079) return 10;
  else return 11;
}

void loop() {
  float tensao = lerTensao();
  int uvIndex = calcularUVIndex(tensao);

  Serial.print("Tensao: ");
  Serial.print(tensao, 3);
  Serial.print(" V | UV Index: ");
  Serial.println(uvIndex);

  delay(1000);
}
