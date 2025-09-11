#ifndef DEVICE_H
#define DEVICE_H
#include <Arduino.h>
#include "../../globals/constants.h"
#include "../../globals/functions.h"
#include "../../utils/text/index.h"
#include "settings/index.h"

#include "../server/index.h"
#include "../logs/index.h"
#include "../sensors/index.h"
#include "../telemetry/index.h"


class Device{
  public:
    const byte mode = MASTER_MODE;
    unsigned long startTime;
    Settings settings;
    Text<12> id;

    Telemetry<Device> telemetry;
    EspServer<Device> server;
    Sensors<Device> sensors;
    Logs<Device> logs;

    Device():
        telemetry(this),
        logs(this),
        sensors(this),
        server(this){}

    void setup(){
        snprintf(id.buffer, sizeof(id.buffer), "%04X%08X", (uint16_t)(ESP.getEfuseMac() >> 32), (uint32_t)ESP.getEfuseMac());
        Serial.print("Device Started: "); Serial.print(id.get());
        settings.import();
        logs.setup();
        
        if(mode == MASTER_MODE)
            Serial.println("Modo Master Ativo");
        
        if(mode == SLAVE_MODE)
            Serial.println("Modo Slave Ativo");

        if(mode == MISTER_MODE)
            Serial.println("Modo Misto Ativo");

        if(mode == MASTER_MODE || mode == MISTER_MODE)
            server.connect();
        
        if(mode == SLAVE_MODE || mode == MISTER_MODE)
            sensors.setup();
    }

    void reset(){
        ESP.restart();
    }
};


inline Device device;
#endif