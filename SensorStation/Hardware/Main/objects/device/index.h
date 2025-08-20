#ifndef DEVICE_H
#define DEVICE_H
#include <Arduino.h>
#include "../../globals/constants.h"
#include "../../globals/functions.h"
#include "../../utils/text/index.h"
#include "settings.h"


class Device{
  public:
    const byte mode = MISTER_MODE;
    Settings settings;
    Text<12> id;
    unsigned long startTime;
    
    Device(){
        startTime = time();
        id.concat(getID());
    }

    void setup(){
        sleep(1000);
        Serial.println("Device Started: " + getID());
        
        if(mode == MASTER_MODE)
            Serial.println("Modo Master Ativo");
        
        if(mode == SLAVE_MODE)
            Serial.println("Modo Slave Ativo");

        if(mode == MISTER_MODE)
            Serial.println("Modo Misto Ativo");

        settings.import();
    }

    unsigned long time(){
        return esp_timer_get_time()/1000;
    }

    float alive(){
        return (time() - startTime)/1000.0;
    }

    void sleep(const int timeout){
        delay(timeout);
    }
    
    void reset(){
        ESP.restart();
    }

    String getID() {
        char chip_id[17];
        snprintf(chip_id, sizeof(chip_id), "%04X%08X",
                (uint16_t)(ESP.getEfuseMac() >> 32),
                (uint32_t)ESP.getEfuseMac());
        return String(chip_id);
    }
};

inline Device device;
#endif