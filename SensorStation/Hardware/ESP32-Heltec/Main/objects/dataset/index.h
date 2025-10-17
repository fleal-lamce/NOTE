#ifndef DATASET_H
#define DATASET_H
#include <Arduino.h>
#include "../../utils/json/index.h"
#include "../../utils/text/index.h"
#define VARS_SIZE 10


struct __attribute__((packed)) DeviceData{
    char id[12];
    float values[VARS_SIZE];
};

class Dataset{
  public:
    DeviceData info;

    Dataset(){
        for(int x=0; x<VARS_SIZE; x++)
            info.values[x] = -1;
    }

    void setID(const char* text){
        strncpy(info.id, text, sizeof(info.id) - 1);
        info.id[sizeof(info.id) - 1] = '\0';
    }

    String toString(){
        Json<256> request;
        request.set("esp_id", info.id);

        Text<128> data = "[";
        for(int x=0; x<VARS_SIZE; x++)
            data += String(info.values[x]) + ",";
        
        data += "]";
        request.set("variables", data.buffer);
        return request.toString();
    }
};

inline Dataset dataset;
#endif