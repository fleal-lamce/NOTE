/***************************************************************************
  This is a library for the BME280 humidity, temperature & pressure sensor

  Designed specifically to work with the Adafruit BME280 Breakout
  ----> http://www.adafruit.com/products/2650

  These sensors use I2C or SPI to communicate, 2 or 4 pins are required
  to interface. The device's I2C address is either 0x76 or 0x77.

  Adafruit invests time and resources providing this open source code,
  please support Adafruit andopen-source hardware by purchasing products
  from Adafruit!

  Written by Limor Fried & Kevin Townsend for Adafruit Industries.
  BSD license, all text above must be included in any redistribution
  See the LICENSE file for details.
 ***************************************************************************/

#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME280 bme; // I2C
//Adafruit_BME280 bme(BME_CS); // hardware SPI
//Adafruit_BME280 bme(BME_CS, BME_MOSI, BME_MISO, BME_SCK); // software SPI

unsigned long delayTime;

void setup() {
    Serial.begin(9600);
    Serial.println(F("BME280 test"));

    if (! bme.begin(0x76, &Wire)) {
        Serial.println("Could not find a valid BME280 sensor, check wiring!");
        while (1);
    }
    
}


void loop() {

    Serial.println("----------------------------------------------------");
    Serial.println("A) Default Test");
    Serial.println("B) Weather Station Scenario");
    Serial.println("C) Humidity Sensing Scenario");
    Serial.println("D) Indoor Navigation Scenario");
    Serial.println("E) Gaming Scenario");
    Serial.println("----------------------------------------------------");
    
    Serial.println("   | mode   | temp | humi | pres | filter | standby | Temperat | Humidity| Pressure    |");
    
    // default mode
    Serial.print("A) | normal | 16x  | 16x  | 16x  | off    |  0.5ms  | ");
    bme.setSampling(Adafruit_BME280::MODE_NORMAL,
                    Adafruit_BME280::SAMPLING_X16,  // temperature
                    Adafruit_BME280::SAMPLING_X16,  // pressure
                    Adafruit_BME280::SAMPLING_X16,  // humidity
                    Adafruit_BME280::FILTER_OFF,
                    Adafruit_BME280::STANDBY_MS_0_5 );
    delayTime = 5000;
    
    printValues();
    delay(delayTime);

    
    // For more details on the following scenarious, see chapter
    // 3.5 "Recommended modes of operation" in the datasheet
    

    // weather monitoring
    Serial.print("B) | forced |  1x  |  1x  |  1x  | off    | 60s     | ");
    bme.setSampling(Adafruit_BME280::MODE_FORCED,
                    Adafruit_BME280::SAMPLING_X1, // temperature
                    Adafruit_BME280::SAMPLING_X1, // pressure
                    Adafruit_BME280::SAMPLING_X1, // humidity
                    Adafruit_BME280::FILTER_OFF   );
                      
    // suggested rate is 1/60Hz (1m)
    delayTime = 6000; // in milliseconds

    // Only needed in forced mode! In normal mode, you can remove the next line.
    bme.takeForcedMeasurement(); // has no effect in normal mode
    
    printValues();
    delay(delayTime);

    
    // humidity sensing
    Serial.print("C) | forced |  1x  |  1x  |  0x  | off    |  1s     | ");
    bme.setSampling(Adafruit_BME280::MODE_FORCED,
                    Adafruit_BME280::SAMPLING_X1,   // temperature
                    Adafruit_BME280::SAMPLING_NONE, // pressure
                    Adafruit_BME280::SAMPLING_X1,   // humidity
                    Adafruit_BME280::FILTER_OFF );
                      
    // suggested rate is 1Hz (1s)
    delayTime = 1000;  // in milliseconds

    // Only needed in forced mode! In normal mode, you can remove the next line.
    bme.takeForcedMeasurement(); // has no effect in normal mode

    printValues();
    delay(delayTime);
    
    
    // indoor navigation
    Serial.print("D) | forced |  2x  | 16x  |  1x  | 16x    |  0.5ms  | ");
    bme.setSampling(Adafruit_BME280::MODE_NORMAL,
                    Adafruit_BME280::SAMPLING_X2,  // temperature
                    Adafruit_BME280::SAMPLING_X16, // pressure
                    Adafruit_BME280::SAMPLING_X1,  // humidity
                    Adafruit_BME280::FILTER_X16,
                    Adafruit_BME280::STANDBY_MS_0_5 );
    
    // suggested rate is 25Hz
    // 1 + (2 * T_ovs) + (2 * P_ovs + 0.5) + (2 * H_ovs + 0.5)
    // T_ovs = 2
    // P_ovs = 16
    // H_ovs = 1
    // = 40ms (25Hz)
    // with standby time that should really be 24.16913... Hz
    delayTime = 41;
    
    // Only needed in forced mode! In normal mode, you can remove the next line.
    bme.takeForcedMeasurement(); // has no effect in normal mode

    printValues();
    delay(delayTime);
    
    
    // gaming
    Serial.print("E) | normal |  1x  |  4x  |  0x  | 16x    |  0.5ms  | ");
    bme.setSampling(Adafruit_BME280::MODE_NORMAL,
                    Adafruit_BME280::SAMPLING_X1,   // temperature
                    Adafruit_BME280::SAMPLING_X4,   // pressure
                    Adafruit_BME280::SAMPLING_NONE, // humidity
                    Adafruit_BME280::FILTER_X16,
                    Adafruit_BME280::STANDBY_MS_0_5 );
                      
    // Suggested rate is 83Hz
    // 1 + (2 * T_ovs) + (2 * P_ovs + 0.5)
    // T_ovs = 1
    // P_ovs = 4
    // = 11.5ms + 0.5ms standby
    delayTime = 12;

    // Only needed in forced mode! In normal mode, you can remove the next line.
    bme.takeForcedMeasurement(); // has no effect in normal mode

    printValues();
    delay(delayTime);
}


void printValues() {
    //Serial.print("Temperature = ");
    Serial.print(bme.readTemperature());
    Serial.print(" °C | ");

    //Serial.print("Humidity = ");
    Serial.print(bme.readHumidity());
    Serial.print(" % |");
    
    //Serial.print("Pressure = ");
    Serial.print(bme.readPressure() / 100.0F);
    Serial.print(" hPa | ");

    //Serial.print("Approx. Altitude = ");
    //Serial.print(bme.readAltitude(SEALEVELPRESSURE_HPA));
    //Serial.print(" m   ");

    Serial.println();
}
