#ifndef PROTOCOL_H
#define PROTOCOL_H
#include <Arduino.h>


template <typename Parent> class Protocol{
  public:
    Parent* device;

    Protocol(Parent* dev):
        device(dev){}
    
    bool handle(){
        device->telemetry.serial.clean();
        device->telemetry.serial.print();

        if(device->telemetry.serial.command.length() > 100)
            return false;

        if(device->telemetry.serial.command.contains("D:")){
            handleID();
            return true;
        }

        if(device->telemetry.serial.command.contains("F:")){
            handleConfig();
            return true;
        }

        if(device->telemetry.serial.command.contains("$MICRS!")){
            device->reset();
            return true;
        }

        if(device->telemetry.serial.command.contains("settings")){
            device->telemetry.serial.send(device->settings.params.toString());
            return true;
        }

        if(device->telemetry.serial.command.contains("$ERASE!")){
            device->settings.erase(); 
            device->reset();
        }

        device->telemetry.serial.reset();
        return false;
    }

    void handleID(){
        const int start = device->telemetry.serial.command.find(':');
        const int end   = device->telemetry.serial.command.find('$');

        if(start == -1 || end == -1)
            {device->telemetry.response.set("ERROR"); return;}
        
        auto key   = device->telemetry.serial.command.substring(start+1, end);
        auto value = device->settings.template get<const char*>(key.get());

        if(value == nullptr)
            {device->telemetry.response.set("ERROR"); return;}

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
            {device->telemetry.response.set("NONE"); return;}

        auto key   = device->telemetry.serial.command.substring(start+1, mid);
        auto value = device->telemetry.serial.command.substring(mid+1, end);

        device->settings.params.set(key.get(), value.get());
        device->settings.save();
        device->telemetry.response.set("OK");
    }
};


#endif