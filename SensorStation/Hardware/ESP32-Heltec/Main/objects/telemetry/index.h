#ifndef TELEMETRY_H
#define TELEMETRY_H
#include "serial/index.h"
#include "protocol/index.h"
#include "modes/QML201C/index.h"
#define MAX_SIZE 1024 


template <typename Parent> class Telemetry{
  private:
    const bool debug = true;
    Parent* device;

  public:
    NextSerial<MAX_SIZE> serial{Serial};
    Protocol<Parent> protocol;
    Text<64> response;

    QML201C<Parent> qml;
    byte type;
    
    Telemetry(Parent* dev):
        device(dev),
        protocol(dev),
        qml(dev){}

    void setup(){
        type = device->settings.template get<byte>("telemetry");
        
        if(type == QML_TEL)
           qml.setup();
        
        response.reset(); 
    }

    void handle(){
        listen();

        if(type == QML_TEL)
            qml.handle();
    }
    
    void listen(){
        serial.listen();
        
        if(type == QML_TEL)
            qml.check();

        if(serial.available)
            protocol.check();
        
        if(response.length() > 0)
            event(response.get());

        serial.reset();
    }
    
    void event(const char* value){
        serial.send(value, true);
        response.reset();
    }
};

#endif