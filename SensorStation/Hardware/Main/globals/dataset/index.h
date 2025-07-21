#ifndef DATASET_H
#define DATASET_H
#include <Arduino.h>
#include "../../utils/json/index.h"


struct __attribute__((packed)) DeviceData{
    char id[12];
    uint8_t area = 1;
    int16_t temperature;
    uint8_t humidity; 
    int16_t sodium; 
    int16_t potassium; 
};

class Dataset{
    public:
    DeviceData info;

    void setID(const char* text){
        strncpy(info.id, text, sizeof(info.id) - 1);
        info.id[sizeof(info.id) - 1] = '\0';
    }

    String toString(){
        JsonDocument variables;
        JsonDocument log;
        JsonDocument request;

        variables["temperature"] = info.temperature;
        variables["humidity"]    = info.humidity;

        log["esp_id"] = info.id;
        log["data"]   = variables;

        request["table"] = "logs";
        request["data"]  = log;
        
        String payload; serializeJson(request, payload);
        return payload;
    }
};

inline Dataset dataset;
#endif