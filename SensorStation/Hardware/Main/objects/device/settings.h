#ifndef SETTINGS_H
#define SETTINGS_H
#include "../utils/json/index.h"


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
        
        Serial.println("Standard Settings Imported");
        params.parse(standard());
        params.save("settings");
    }

    const char* standard(){
        return R"({
            "active": true,
            "ssid": "ABCDEF",
            "pass": "EFGHI",
            "channel": 5
        })";
    }
};

#endif