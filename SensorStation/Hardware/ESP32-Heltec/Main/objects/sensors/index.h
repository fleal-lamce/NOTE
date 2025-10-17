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
    WindStation windstation = WindStation(23, 42);
    RainStation rain = RainStation(15);
    DHTSensor dht = DHTSensor(36);
    SHT30 sht = SHT30(4, 15);
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

        dataset.info.values[0] = windstation.velocity.value;
        available = true;
    }
};

#endif