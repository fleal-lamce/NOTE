#ifndef SETTINGS_H
#define SETTINGS_H
#include "../../utils/json/index.h"


class Settings{
  public:
    Json<512> params;

    void import(){
        params.download("settings");
        delay(500);

        if(!params.empty()){
            Serial.println("Settings Downloaded");
            return params.print();
        }
        
        erase();
    }

    template<typename T> T get(const char* key) const {
        return params.template get<T>(key);
    }

    const char* getID(){
        static char buffer[20];
        snprintf(buffer, sizeof(buffer), "%04X%08X", (uint16_t)(ESP.getEfuseMac() >> 32), (uint32_t)ESP.getEfuseMac());
        return buffer;
    }

    void save(){
        params.save("settings");
    }

    void erase(){
        Serial.println("Standard Settings Imported");
        params.parse(standard());
        save();
    }
    
    const char* standard(){
        return R"({
            "ssid": "Klauss",
            "pass": "12345678",
            "server": "http://192.168.249.12:8000/api/";
            "channel": 5
        })";
    }
};

#endif