#ifndef dhtsensor_H
#define dhtsensor_H
#include <Arduino.h>
#include <DHT.h>
#include "../../../utils/listener/index.h"
#include "../../../utils/time/index.h"


#define SAMPLE_TIME 200
#define USE_SAMPLE  true


class DHTSensor{  
  private:
    class Temperature{
      public:
        float value; 
        bool working;
        DHT& dht;

        Temperature(DHT& _dht): 
            dht(_dht){}

        void update(){
            value   = sample(SAMPLE_TIME);
            working = (value != 999);
        }

        float get(){
            float current = dht.readTemperature();

            if(isnan(current) || abs(current) > 100)
                return 999;

            return current;
        }

        float sample(const int timeout){
            const unsigned long startTime = Time::get();

            while(Time::get() - startTime < timeout){
                const float current = get();

                if (current == 999)
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
        float value;
        bool working;
        DHT& dht;

        Humidity(DHT& _dht): 
            dht(_dht){}

        void update(){
            value   = sample(SAMPLE_TIME);
            working = (value != 999);
        }

        float get(){
            float current = dht.readHumidity();

            if (isnan(current) || abs(current) > 100)
                return 999;

            return current;
        }

        float sample(const int timeout){
            const unsigned long startTime = Time::get();

            while (Time::get() - startTime < timeout) {
                const float current = get();

                if (current == 999)
                    continue;

                return current;
            }

            return 999;
        }

        String toString(){
            return String(value) + "%";
        }
    };

  public:
    DHT dht;
    Temperature temperature = Temperature(dht);
    Humidity humidity = Humidity(dht);

    DHTSensor(uint8_t pin): 
        dht(pin, DHT22){}

    void setup(){
        dht.begin();
        delay(2000); 
    }

    void handle(){
        static Listener listener = Listener(5000);

        if(!listener.ready())
            return;

        temperature.update();
        humidity.update();
        Serial.println("dht temp: " + String(temperature.value));
        Serial.println("dht humy: " + String(humidity.value));
    }
};

#endif