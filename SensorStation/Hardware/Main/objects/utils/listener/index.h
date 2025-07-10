#ifndef LISTENER_H
#define LISTENER_H
#include <Arduino.h>


class Listener{
    public:
    unsigned long startTime;
    int timeout = 1000;

    Listener(int _timeout){
        startTime = get();
        timeout   = _timeout;
    }
    
    unsigned long get(){
        return esp_timer_get_time()/1000;
    }

    void set(int _timeout){
        timeout = _timeout;
    }

    void reset(){
        startTime = get();
    }

    bool ready(){
        if(get() - startTime < timeout)
            return false;

        startTime = get();
        return true;
    }
};

#endif