#ifndef SHT30_H
#define SHT30_H
#include <Arduino.h>
#include <Wire.h>

#include "../../../utils/listener/index.h"
// USO 3 a 5 Volts, Branco = SDA, Amarelo = SCL


class SHT30{
  private:
    class Temperature{
      public:
        float value;
        bool working;

        void update(const uint16_t rawT){
            value   = -45.0f + 175.0f * rawT  / 65535.0f;
            working = true;
        }

        String toString(){
            return String(value) + "ºC";
        }
    };

    class Humidity{
      public:
        float value;
        bool working;

        void update(const uint16_t rawRH){
            value   = 100.0f * rawRH / 65535.0f;
            working = true;
        }

        String toString(){
            return String(value) + "%";
        }
    };

  public:
    Temperature temperature = Temperature();
    Humidity humidity = Humidity();
    int sda, scl;

    const uint8_t CMD_MEAS_HR[2] = {0x2C, 0x06}; 
    const uint8_t CMD_RESET[2]   = {0x30, 0xA2};
    const uint8_t SHT30_ADDR     = 0x44;

    SHT30(int sda_pin, int scl_pin):
        sda(sda_pin),
        scl(scl_pin){}
    
    void setup(){
        Serial.println("sda: " + String(sda) + " | scl: " + String(scl));
        Wire.begin(sda, scl);
        Wire.setTimeout(5000);
        Wire.setClock(50000);
        check();
        reset();
    }

    void check(){
        Serial.println("Scanning i2c...");
        byte count=0;

        for (byte addr=1; addr<127; addr++){
            Wire.beginTransmission(addr);

            if (Wire.endTransmission() != 0)
                continue;

            Serial.print("I2C device at 0x"); Serial.println(addr, HEX);
            count++;
        }

        if(count > 0)
            return;
        
        Serial.println("No I2C devices found");
    }

    uint8_t extract(const uint8_t *data, uint8_t len) {
        uint8_t crc = 0xFF;

        for (uint8_t i = 0; i < len; i++) {
            crc ^= data[i];

            for (uint8_t bit = 0; bit < 8; bit++) {
                if (crc & 0x80) 
                    crc = (crc << 1) ^ 0x31;
                else 
                    crc <<= 1;
                
                crc &= 0xFF; 
            }
        }
        
        return crc;
    }

    bool request() {
        Wire.beginTransmission(SHT30_ADDR);
        Wire.write(CMD_MEAS_HR, 2);
        
        if(Wire.endTransmission() != 0)
            return false;

        delay(20);

        if(Wire.requestFrom(SHT30_ADDR, (uint8_t)6) != 6) 
            return false;

        delay(20); 
        return true;
    }

    void reset() {
        Wire.beginTransmission(SHT30_ADDR);
        Wire.write(CMD_RESET, 2);
        Wire.endTransmission();
        delay(10);
    }

    bool update(){
        temperature.working = false;
        humidity.working    = false;

        if(!request())
            return false;
        
        if(Wire.available() != 6)
            return false;
        
        uint8_t raw[6];
        for(uint8_t i = 0; i < 6; i++)
            raw[i] = Wire.read();
        
        uint8_t crcT_calc  = extract(raw, 2);
        uint8_t crcRH_calc = extract(raw + 3, 2);
        
        const bool fail1 = (crcT_calc != raw[2]);
        const bool fail2 = (crcRH_calc != raw[5]);

        if(fail1 || fail2)
            return false;

        const uint16_t rawT  = (raw[0] << 8) | raw[1];
        const uint16_t rawRH = (raw[3] << 8) | raw[4];

        temperature.update(rawT);
        humidity.update(rawRH);
        return true;
    }

    void handle(){
        static Listener listener = Listener(5000);

        if(!listener.ready())
            return;

        update();

        Serial.println("temperatura: " + temperature.toString());
        Serial.println("umidade: " + humidity.toString());
    }
};

#endif