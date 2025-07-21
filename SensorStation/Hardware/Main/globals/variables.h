#ifndef VARIABLES_H
#define VARIABLES_H
#include <Arduino.h>
#include <ArduinoJson.h>


struct Variables{
    const char* firmware  = "v1.0.0";
    const bool temp_debug = false;
    const bool serial_debug = false;
};

inline Variables vars;
#endif