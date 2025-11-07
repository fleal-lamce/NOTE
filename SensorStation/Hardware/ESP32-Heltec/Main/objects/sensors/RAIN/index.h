#ifndef RAIN_H
#define RAIN_H
#include <Arduino.h>
#include "../../../utils/listener/index.h"

#define BUCKET_SIZE_MM 0.3f // mm por basculada
#define DEBOUNCE_MS    500  // tempo mínimo entre pulsos


class RainStation{
  public:
    unsigned long lastTime = Time::get();
    int pin;
    int counter;
    float value;
    
    RainStation(int _pin):
        pin(_pin){}

    void setup(){
        
    }

    void handle(){
        static Listener listener = Listener(120000);
        static bool state  = false;
        const bool signal  = (analogRead(pin) < 4000);
        
        if(signal != state && (Time::get() - lastTime) > 300){
            if(signal){
                counter++;
                Serial.println("rain count: " + String(counter));
            }
            
            state    = signal;
            lastTime = Time::get();
        }

        if(listener.ready(false)){
            const float t = listener.getSec();
            listener.reset();

            value   = ((float) counter)/t;
            counter = 0;
        }
    }
};

#endif