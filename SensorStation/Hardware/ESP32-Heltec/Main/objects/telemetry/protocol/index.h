#ifndef PROTOCOL_H
#define PROTOCOL_h
#include <Arduino.h>


template <typename Parent> class Protocol{
  public:
    Parent* device;

    Protocol(Parent* dev):
        device(dev){}

    void check(){
        device->telemetry.serial.clean();

        if(device->telemetry.serial.command.contains("D:"))
            return handleID();

        if(device->telemetry.serial.command.contains("F:"))
            return handleConfig();
        
        if(device->telemetry.serial.command.contains("$MICRS!"))
            return device->reset();

        if(device->telemetry.serial.command.contains("$erase!")){
            device->settings.erase(); 
            return device->reset();
        }

        if(device->telemetry.serial.command.contains("$CHECK!")){
            device->telemetry.response.set("OK");
            return;
        }
    }

    void handleID(){
        const int start = device->telemetry.serial.command.find(':');
        const int end   = device->telemetry.serial.command.find('$');

        if(start == -1 || end == -1)
            return device->telemetry.response.set("ERROR");
        
        auto key   = device->telemetry.serial.command.substring(start+1, end);
        auto value = device->settings.template get<String>(key.get());
        
        if(value == nullptr)
            return device->telemetry.response.set("ERROR");

        device->telemetry.response.reset();
        device->telemetry.response += '$';
        device->telemetry.response += (value);
        device->telemetry.response += '!';
    }

    void handleConfig(){
        const int start = device->telemetry.serial.command.find(':');
        const int mid   = device->telemetry.serial.command.find('$');
        const int end   = device->telemetry.serial.command.find('!');

        if(start == -1 || mid == -1 || end == -1)
            return device->telemetry.response.set("NONE");

        auto key   = device->telemetry.serial.command.substring(start+1, mid);
        auto value = device->telemetry.serial.command.substring(mid+1, end);

        device->settings.params.set(key.get(), value.get());
        device->telemetry.response.set("OK");
        device->settings.save();
    }
};

#endif