#ifndef PROTOCOL_H
#define PROTOCOL_H
#include <Arduino.h>
#include "../../device/index.h"
#include "../../../utils/text/index.h"
#include "../../serial/index.h"


class Protocol{
  public:
    NextSerial<64> serial = NextSerial<64>(Serial);
    Text<64> response;

    void handle(){
        serial.listen();

        if(!serial.available)
            return;

        serial.command.remove(' ');
        serial.command.remove('\r');
        serial.command.remove('\n');
        serial.command.remove('\t');
        
        if(serial.command.length() < 5 || serial.command.length() > 50)
            return;

        Serial.println("(serial) command:  " + serial.command.toString());
        processResponse();
        
        Serial.print("(serial) response: ");
        serial.uart.write(response.get());
        serial.uart.write("\r\n");
        serial.reset();
    }
    
    void processResponse(){     
        if(serial.command.contains("D:"))
            return handleID();

        if(serial.command.contains("F:"))
            return handleConfig();

        return handleStandard();
    }

    void handleID(){
        const int start = serial.command.find(':');
        const int end   = serial.command.find('$');

        if(start == -1 || end == -1)
            {response = "ERROR"; return;}
        
        auto key   = serial.command.substring(start+1, end);
        auto value = device.settings.params.get<const char*>(key.get());

        if(value == nullptr)
            {response = "ERROR"; return;}

        response.reset();
        response += '$';
        response += (value);
        response += '!';
    }

    void handleConfig(){
        const int start = serial.command.find(':');
        const int mid   = serial.command.find('$');
        const int end   = serial.command.find('!');

        if(start == -1 || mid == -1 || end == -1)
            {response = "NONE"; return;}

        auto key   = serial.command.substring(start+1, mid);
        auto value = serial.command.substring(mid+1, end);

        device.settings.params.set(key.get(), value.get());
        device.settings.save();
        response = "OK";
    }

    void handleStandard(){
        if(serial.command.contains("$CHECK!")){
            response = "OK";
            return;
        }

        if(serial.command.contains("$ERASE!")){
            device.settings.erase();
            delay(1500);
            return device.reset();
        }

        if(serial.command.contains("$MICRS!")){
            Serial.println("reiniciando dispositivo");
            delay(1500);
            return device.reset();
        }

        if(serial.command.contains("settings")){
            response = "OK";
            return device.settings.params.print();
        }

        response = "NONE";
    }
};

inline Protocol protocol;
#endif