#ifndef SHT30_H
#define SHT30_H
#include <Arduino.h>
#include <Wire.h>

#include "../../../utils/listener/index.h"
// USO 3 a 5 Volts, Amarelo = SCL, Branco = SDA


class SHT30{
    private:
    class Temperature{
        public:
        float value;
        bool working;

        void update(const uint16_t rawT){
            value = -45.0f + 175.0f * rawT  / 65535.0f;
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
            value = 100.0f * rawRH / 65535.0f;
        }

        String toString(){
            return String(value) + "%";
        }
    };

    public:
    Temperature temperature = Temperature();
    Humidity humidity = Humidity();
    int sda, scl;

    SHT30(int sda_pin, int scl_pin):
        sda(sda_pin),
        scl(scl_pin){}
    
    void setup(){
        Serial.println("sda: " + String(sda) + " | scl: " + String(scl));
        Wire.begin(sda, scl);
        Wire.setTimeout(5000);
    }

    uint8_t extract(const uint8_t *data, uint8_t len){
        uint8_t address = 0xFF;
        for(uint8_t i = 0; i < len; i++){
            address ^= data[i];
            
            for(uint8_t b = 0; b < 8; b++)
                address = (address & 0x80) ? (address << 1) ^ 0x31 : (address << 1);
        }
        return address;
    }

    bool requestData(){
        const uint8_t CMD_MEAS_HR[2] = {0x2C, 0x06}; 
        const uint8_t SHT30_ADDR = 0x44;  

        Wire.beginTransmission(SHT30_ADDR);
        Wire.write(CMD_MEAS_HR, 2);
        
        if(Wire.endTransmission() != 0)
            return false;
        
        delay(20);
        Wire.requestFrom(SHT30_ADDR, (uint8_t) 6);
        return true;
    }

    bool update(){
        if(!requestData())
            return false;

        if(Wire.available() != 6)
            return false;
        
        uint8_t raw[6];
        for(uint8_t i = 0; i < 6; i++)
            raw[i] = Wire.read();
        
        const bool fail1 = (extract(raw, 2) != raw[2]);
        const bool fail2 = (extract(raw + 3, 2) != raw[5]);

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
    }
};

#endif