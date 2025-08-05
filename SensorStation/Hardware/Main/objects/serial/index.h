#ifndef SERIAL_H
#define SERIAL_H
#include <Arduino.h>
#include "../../utils/text/index.h"
#include "../device/index.h"
#include "../../utils/listener/index.h"

#define CMD_MIN_SIZE 5
#define IS_DEBUG false


template<int CMD_SIZE> class NextSerial{
  public:
    Text<CMD_SIZE> command;
    bool available = false;
    int timeout    = 5000; 
    Stream& uart;

    NextSerial(Stream& ser):
        uart(ser){}

    void listen(){
        static Listener listener = Listener(100);
        
        if(!listener.ready())
            return;

        const int size  = uart.available();
        const bool junk = (size < CMD_MIN_SIZE || size > CMD_SIZE);

        if(size == 0)
            return;
        
        if(!junk)
            reset();
        
        const unsigned long startTime = device.time();
        while(uart.available() && device.time() - startTime < 5000){
            const char letter = (char) uart.read();
            
            if(junk)
                continue;

            command.concat(letter);
            delay(1);
        }
        
        available = (command.length() > 5 && !command.isEmpty());
    }
    
    void reset(){
        command.reset();
        available = false;
    }
};

#endif