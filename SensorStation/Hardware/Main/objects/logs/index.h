#ifndef SERVER_LOGS_H
#define SERVER_LOGS_H
#include "../../globals/constants.h"
#include "../../globals/variables.h"
#include "../../globals/functions.h"
#include "../utils/listener/index.h"
#include "../utils/json/index.h"
#include "../device/index.h"
#include "../utils/notes/index.h"
#include "../server/index.h"
#include "../sensors/index.h"
#include "../telemetry/heltec/index.h"

#define REQUEST_SIZE  (1024) 
#define LOGS_SIZE     (REQUEST_SIZE - 50)
#define VARIABLE_SIZE (LOGS_SIZE - 50) 

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
    Notes notes = Notes("/logs.txt");

    void setup(){
        Serial.println("Setting Up Notes");
        delay(2000);
        notes.setup();
    }

    void handle(){
        update();
        upload();
    }

    void update(){
        static Listener listener(15000);

        if(!listener.ready())
            return;
        
        if(!device.master)
            return;
        
        if(heltec.get(sensors.data))
            return send();
    }

    void upload(){
        static Listener listener(60000);

        if(!listener.ready())
            return;

        if(!server.active)
            return;

        while(notes.length() > 10){          
            auto log = get(); 
            String result = server.post("add/", log.toString());
            Serial.println("(server) log:      " + log.toString());
            Serial.println("(server) response: " + result);
            Serial.println();
            
            if(result == "-1")
                break;

            notes.droplines(1);
            delay(200);
        }
    }

    void send(){
        const int size = notes.length();
        auto log = get();

        Serial.println("(log) stored:     " + log.toString());
        Serial.println("(log) notes size: " + String(size));
        Serial.println();
        
        if(size > 5000)
            notes.droplines(5);

        notes.append(log.toString());
    }

    Json<REQUEST_SIZE> get(){
        Json<REQUEST_SIZE>  request;
        Json<LOGS_SIZE>     log;
        Json<VARIABLE_SIZE> variables;

        variables.set("temperature", sensors.data.temperature);
        variables.set("humidity", sensors.data.humidity);
        
        log.set("esp_id", sensors.data.id);
        log.set("data", variables.data);
        
        request.set("table", "logs");
        request.set("data", log.data);
        return request;
    }
};


inline Logs logs;
#endif