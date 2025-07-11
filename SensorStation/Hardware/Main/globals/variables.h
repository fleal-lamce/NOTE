#ifndef VARIABLES_H
#define VARIABLES_H
#include <Arduino.h>
#include <ArduinoJson.h>


struct __attribute__((packed)) DeviceData{
    char id[12];
    uint8_t area = 3;
    int16_t temperature;
    uint8_t humidity; 
    int16_t sodium; 
    int16_t potassium; 
};

struct Variables{
    const char* firmware  = "v1.0.0";
    const bool temp_debug = false;
    const bool serial_debug = false;
};

inline Variables vars;
#endif