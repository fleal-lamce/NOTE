#ifndef SENSORS_H
#define SENSORS_H
#include <Arduino.h>
#include <Arduino.h>
#include "../../globals/dataset/index.h"
#include "../device/index.h"
#include "../../utils/listener/index.h"
#include "DHT22/index.h"
#include "SHT30/index.h"


class Sensors{
    public:
    DHTSensor dht = DHTSensor(36);
    SHT30 sht = SHT30(45, 46);
    bool available;

    void setup(){
        dataset.setID(device.id.get());
        dht.setup();
        sht.setup();
    }

    void update(){
        dht.update();
        sht.update();

        dataset.info.temperature = sht.temperature; //dht.temperature.value;
        dataset.info.humidity    = sht.humidity;    //dht.humidity.value;
        available = true;
    }

    void handle(){
        static Listener listener(5000);

        if(!listener.ready() || device.master)
            return;
           
        update();
    }
};

inline Sensors sensors;
#endif