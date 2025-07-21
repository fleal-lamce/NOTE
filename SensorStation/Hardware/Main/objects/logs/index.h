#ifndef SERVER_LOGS_H
#define SERVER_LOGS_H
#include "../../globals/dataset/index.h"
#include "../device/index.h"
#include "../../utils/notes/index.h"
#include "../telemetry/heltec/index.h"
#include "../sensors/index.h"
#include "../server/index.h"


/*
REQUEST FORMAT (SERVER)
{
    "table": "logs",
    "data": {
        "esp_id": "MICTALTALTAL",
        "data":  "{a: 1, b: 2, c: 3}"
    }
}
*/

class Logs{
    public:
    Notes notes = Notes("/txt");

    void setup(){
        Serial.println("Setting Up Notes");
        delay(2000);
        notes.setup();
    }

    void handle(){
        if(!device.master)
            return handleSender();

        handleStore();
        handleServer();
    }

    void handleSender(){
        static Listener listener = Listener(5000);
        
        if(!listener.ready())
            return;

        if(!sensors.available)
            return;

        heltec.send(dataset.info); 
        sensors.available = false;
        Serial.println("(log) sent: " + dataset.toString());
    }

    void handleStore(){
        static Listener listener = Listener(5000);
        
        if(!listener.ready())
            return;

        if(!heltec.get(dataset.info))
            return;
        
        store();
    }

    void handleServer(){
        static Listener listener = Listener(30000);
        
        if(!listener.ready())
            return;

        if(!server.active)
            return;
        
        send();
    }

    void store(){
        const int size = notes.length();
        String log = dataset.toString();

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
            String result = server.post("add/", log);
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


inline Logs logs;
#endif