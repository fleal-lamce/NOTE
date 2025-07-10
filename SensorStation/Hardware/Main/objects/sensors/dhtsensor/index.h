#ifndef dhtsensor_H
#define dhtsensor_H
#include <Arduino.h>
#include <DHT.h>
#include "../../../globals/variables.h"
#include "../../device/index.h"

#define SAMPLE_TIME 2000
#define DHTPIN  32
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);


class Temperature{
    public:
    int value;
    bool working;

    void update(){
        value   = sample(SAMPLE_TIME);
        working = (value != 999);
    }

    int get(){
        float current = dht.readTemperature();

        if(vars.temp_debug)
            current = 25.0;

        if(isnan(current) || abs(current) > 100)
            return 999;
            
        return current;
    }

    int sample(const int timeout){
        const unsigned long startTime = device.time();

        while(device.time() - startTime < timeout){
            const float current = get();

            if(current == 999)
                continue;

            return current;
        }
        
        return 999;
    }

    String toString(){
        return String(value) + " ºC";
    }
};

class Humidity{
    public:
    int value;
    bool working;

    void update(){
        value   = sample(SAMPLE_TIME);
        working = (value != 999);
    }

    int get(){
        float current = dht.readHumidity();

        if(isnan(current) || abs(current) > 100)
            return 999;

        return current;
    }

    int sample(const int timeout){
        const unsigned long startTime = device.time();

        while(device.time() - startTime < timeout){
            const float current = get();

            if(current == 999)
                continue;

            return current;
        }
        
        return 999;
    }
    
    String toString(){
        return String(value) + "%";
    }
};

class DHTsensor{
    public:
    bool began;
    Temperature temperature;
    Humidity humidity;

    void setup(){
        began = true;
        dht.begin();
        delay(2000);
    }

    void update(){
        if(!began)
            setup();

        temperature.update();
        humidity.update();
    }
};


inline DHTsensor dhtsensor;
#endif