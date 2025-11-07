#ifndef SENSORS_H
#define SENSORS_H
#include <Arduino.h>
#include <Arduino.h>
#include "../dataset/index.h"
#include "../../utils/listener/index.h"
#include "DHT22/index.h"
#include "SHT30/index.h"
#include "WIND/index.h"
#include "RAIN/index.h"

template <typename Parent> class Sensors{
  private:
    Parent* device;
    
  public:
    WindStation windstation = WindStation(13, 4);
    RainStation rain = RainStation(12);
    //DHTSensor dht = DHTSensor(4);
    SHT30 sht = SHT30(8, 9);
    bool available;

    Sensors(Parent* dev):
        device(dev){}

    void setup(){
        dataset.setID(device->id.get());
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
        
        if(!listener.ready() || device->mode == MASTER_MODE)
            return;
        
        dataset.info.values[0] = sht.temperature.value;
        dataset.info.values[1] = sht.humidity.value;
        dataset.info.values[2] = windstation.velocity.value;
        dataset.info.values[3] = windstation.direction.value;
        dataset.info.values[4] = rain.value;
        available = true;
    }
};

#endif