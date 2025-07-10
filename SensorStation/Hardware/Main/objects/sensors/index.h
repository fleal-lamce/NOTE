#ifndef SENSORS_H
#define SENSORS_H
#include <Arduino.h>
#include <Arduino.h>
#include "../../globals/constants.h"
#include "../../globals/variables.h"
#include "../../globals/functions.h"
#include "../device/index.h"
#include "../telemetry/lora/index.h"
#include "../telemetry/espnow/index.h"
#include "../utils/listener/index.h"
#include "dhtsensor/index.h"


class Sensors{
    public:
    DeviceData data;
    
    void setup(){
        strncpy(data.id, device.id.buffer, device.id.index);
    }

    void update(){
        dhtsensor.update();

        data.temperature = dhtsensor.temperature.value;
        data.humidity    = dhtsensor.humidity.value;
        Serial.println(dhtsensor.temperature.toString());
    }

    void handle(){
        static Listener listener(5000);

        if(!listener.ready() || device.master)
            return;

        update();
        device.islora ? lora.send(data) : espnow.send(data);
    }
};

inline Sensors sensors;
#endif