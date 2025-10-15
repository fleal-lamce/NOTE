#ifndef SERVER_LOGS_H
#define SERVER_LOGS_H
#include "../dataset/index.h"
#include "../../utils/notes/index.h"
//#include "../wireless/heltec/index.h"


template <typename Parent> class Logs{
  private:
    //HeltecLora heltec;
    Notes notes = Notes("/txt");
    Parent* device;
    
  public:
    Logs(Parent* dev):
        device(dev){}

    void setup(){
        Serial.println("Setting Up Notes");
        //heltec.setup();
        delay(2000);
        notes.setup();
    }

    void handle(){
        if(device->sending)
            handleSender();
        
        if(device->serving)
            handleServer();

        handleStore();
    }

    void handleSender(){
        static Listener timer = Listener(1*60*1000);
        
        if(!timer.ready())
            return;

        if(!device->sensors.available)
            return;
        
        //heltec.send(dataset.info); 
        device->sensors.available = false;
        Serial.println("(log) sent: " + dataset.toString());
    }

    void handleServer(){
        static Listener timer = Listener(30*1000);
        
        if(!timer.ready())
            return;

        if(!device->server.active)
            return;
        
        while(notes.length() > 10){ 
            String log    = notes.readlines(1);
            String result = device->server.post("api/add_log/", log);
            Serial.println("(server) log:      " + log);
            Serial.println("(server) response: " + result);
            Serial.println();
            
            if(result == "-1")
                break;

            notes.droplines(1);
            delay(200);
        }
    }

    void handleStore(){
        static Listener timer = Listener(5*1000);

        if(!timer.ready())
            return;

        if(device->mode == SLAVE_MODE)
            return;

        //if(device->mode == MASTER_MODE && !heltec.get(dataset.info))
        //    return;

        if(device->mode == MISTER_MODE && !device->sensors.available)
            return;

        const int size = notes.length();
        String log     = dataset.toString();

        Serial.println("(log) stored:     " + log);
        Serial.println("(log) notes size: " + String(size));
        Serial.println();
        
        if(size > 15000)
            notes.droplines(5);

        notes.append(log);
        device->sensors.available = false;
    }
};

#endif