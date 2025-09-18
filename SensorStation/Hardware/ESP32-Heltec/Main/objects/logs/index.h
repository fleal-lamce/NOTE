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
        if(device->mode == SLAVE_MODE  || device->mode == MISTER_MODE)
            handleSender();
        
        if(device->mode == MASTER_MODE || device->mode == MISTER_MODE){
            handleStore();
            handleServer();
        }
    }

    void handleSender(){
        static Listener listener = Listener(5000);
        
        if(!listener.ready())
            return;

        if(!device->sensors.available)
            return;
        
        //heltec.send(dataset.info); 
        device->sensors.available = false;
        Serial.println("(log) sent: " + dataset.toString());
    }

    void handleStore(){
        static Listener listener = Listener(7000);
        
        if(!listener.ready())
            return;

        //if(!heltec.get(dataset.info))
        //    return;
        
        store();
    }

    void handleServer(){
        static Listener listener = Listener(30000);
        
        if(!listener.ready())
            return;

        if(!device->server.active)
            return;
        
        send();
    }

    void store(){
        const int size = notes.length();
        String log     = dataset.toString();

        Serial.println("(log) stored: " + log);
        Serial.println("(log) notes size: " + String(size));
        Serial.println();
        
        if(size > 15000)
            notes.droplines(5);

        notes.append(log);
    }

    void send(){
        while(notes.length() > 10){ 
            String log    = notes.readlines(1);
            String result = device->server.post("add/", log);
            Serial.println("(server) log:      " + log);
            Serial.println("(server) response: " + result);
            Serial.println();
            
            if(result == "-1")
                break;

            notes.droplines(1);
            delay(200);
        }
    }
};

#endif