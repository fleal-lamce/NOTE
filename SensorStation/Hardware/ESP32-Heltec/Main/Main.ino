

#include "globals/constants.h"
#include "globals/functions.h"
#include "utils/text/index.h"

#include "objects/settings/index.h"
#include "objects/server/index.h"
#include "objects/logs/index.h"
#include "objects/sensors/index.h"
#include "objects/telemetry/index.h"


class Device{
  public:
    const byte mode = MISTER_MODE;
    unsigned long startTime;
    Settings settings;
    Text<20> id;

    Telemetry<Device> telemetry;
    EspServer<Device> server;
    Sensors<Device> sensors;
    Logs<Device> logs;

    bool sending = false;
    bool serving = false; 

    Device():
        telemetry(this),
        logs(this),
        sensors(this),
        server(this){}

    void setup(){
        settings.import();
        id.set(settings.template get<const char*>("esp_id"));
        Serial.print("\n\nDevice Started: "); Serial.println(id.get());
        settings.params.print();
        
        sending = (mode == SLAVE_MODE  || mode == MISTER_MODE);
        serving = (mode == MASTER_MODE || mode == MISTER_MODE);
        
        Serial.println(
            (mode == MASTER_MODE) ? "Modo Master Ativo" :
            (mode == SLAVE_MODE)  ? "Modo Slave Ativo"  : "Modo Misto Ativo"
        );

        if(mode == MISTER_MODE)
            Serial.println();

        if(serving)
            server.connect();
        
        if(sending)
            sensors.setup();
        
        telemetry.setup();
        logs.setup();
    }

    void handle(){
        if(sending)
            sensors.handle();
        
        if(serving)
            server.handle();
        
        telemetry.handle();
        logs.handle();
    }

    void reset(){
        ESP.restart();
    }
};


inline Device device;

void setup(){
    Serial.begin(115200); delay(800);
    device.setup();
}

void loop(){
    device.handle();
}
