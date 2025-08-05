#ifndef RAIN_H
#define RAIN_H
#include <Arduino.h>
#include "../../../utils/listener/index.h"

#define BUCKET_SIZE_MM 0.3f // mm por basculada
#define DEBOUNCE_MS    500  // tempo mínimo entre pulsos


class RainStation{
  public:
    int pin;
    int counter;
    float value;
    
    RainStation(int _pin):
        pin(_pin){}

    void setup(){
        pinMode(pin, INPUT_PULLUP);
    }

    void handle(){
        static Listener listener = Listener(15000);
        static bool state  = false;
        const bool signal  = !digitalRead(pin);

        if(signal != state){
            state = signal;

            if(signal)
                counter++;
        }

        if(listener.ready(false)){
            const float t = listener.getSec();
            listener.reset();

            value   = counter/t;
            counter = 0;
            setStatus();
        }
    }
};

#endif