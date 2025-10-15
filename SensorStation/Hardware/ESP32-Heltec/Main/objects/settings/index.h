#ifndef SETTINGS_H
#define SETTINGS_H
#include "../../utils/json/index.h"
#include "../../globals/functions.h"
#include "../../globals/constants.h"


class Settings{
  public:
    Json<1024> params;

    void import(){
        params.download("settings");
        delay(500);

        if(params.empty())
            erase();
    }
    
    template<typename T> T get(const char* key) const {
        return params.template get<T>(key);
    }
    
    void save(){
        params.save("settings");
    }

    void erase(){
        Serial.println("Standard Settings Imported");
        reset();
        save();
    }
    
    void reset(){
        params.data["esp_id"] = getID();
        params.data["server"]    = "https://sighir.com:8000/";
        params.data["telemetry"] = 1;
        params.data["ssid"] = "lamcegrva";
        params.data["pass"] = "aaaaa";
    }

    const char* getID(){
        static char buffer[20];
        snprintf(buffer, sizeof(buffer), "%04X%08X", (uint16_t)(ESP.getEfuseMac() >> 32), (uint32_t)ESP.getEfuseMac());
        return buffer;
    }
};


#endif