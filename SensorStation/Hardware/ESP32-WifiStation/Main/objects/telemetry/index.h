#ifndef TELEMETRY_H
#define TELEMETRY_H
#include "serial/index.h"
#include "protocol/index.h"
#include "multiplexer/index.h"
#define MAX_SIZE 1024 


template <typename Parent> class Telemetry{
  private:
    const bool debug = true;
    Parent* device;

  public:
    NextSerial<MAX_SIZE> serial{debug ? Serial : Serial2};
    Text<64> response;

    Multiplexer<Parent> multiplexer;
    Protocol<Parent> protocol;

    Telemetry(Parent* dev):
        device(dev),
        protocol(dev),
        multiplexer(dev){}

    void setup(){
        if(device->mode == SLAVE_MODE)
            multiplexer.setup();
         
        response.reset(); 
    }

    void handle(){
        serial.listen();

        if(device->mode == SLAVE_MODE)
            multiplexer.handle();
        
        if(serial.available && protocol.handle())
            serial.reset();
        
        if(response.length() > 0)
            event(response.get());
    }

    void event(const char* value){
        Serial.println("(telemetry) event: " + String(value));
        serial.send(value, true);
        response.reset();
    }
};

#endif