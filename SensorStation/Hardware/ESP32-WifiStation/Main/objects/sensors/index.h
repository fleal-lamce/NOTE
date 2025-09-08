#ifndef SENSORS_H
#define SENSORS_H
#include <Arduino.h>
#include <Arduino.h>
#include "../../globals/dataset/index.h"
#include "../device/index.h"
#include "../../utils/listener/index.h"
#include "DHT22/index.h"
#include "SHT30/index.h"
#include "WIND/index.h"
#include "RAIN/index.h"

class Sensors{
  public:
    WindStation windstation = WindStation(23, 42);
    RainStation rain = RainStation(15);
    DHTSensor dht = DHTSensor(36);
    SHT30 sht = SHT30(4, 15);
    bool available;

    void setup(){
        dataset.setID(device.id.get());
        //dht.setup();
        sht.setup();
        windstation.setup();
        rain.setup();
    }

    void handle(){
        static Listener listener(5000);
        windstation.handle();
        sht.handle();
        rain.handle();
        //dht.handle();
        
        if(!listener.ready() || device.mode == MASTER_MODE)
            return;

        dataset.info.temperature = sht.temperature.value; 
        dataset.info.humidity    = sht.humidity.value;  
        dataset.info.velocity    = windstation.velocity.value;
        dataset.info.direction   = windstation.direction.value; 
        dataset.info.rain        = rain.value;
        available = true;
    }
};

inline Sensors sensors;
#endif