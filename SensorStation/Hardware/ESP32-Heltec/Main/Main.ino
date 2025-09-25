

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
    Text<12> id;

    Telemetry<Device> telemetry;
    EspServer<Device> server;
    Sensors<Device> sensors;
    Logs<Device> logs;

    Device():
        telemetry(this),
        logs(this),
        sensors(this),
        server(this){}

    void setup(){
        id.set(settings.getID());
        Serial.print("\n\nDevice Started: "); Serial.println(id.get());
        settings.import();
        logs.setup();
        
        if(mode == MASTER_MODE)
            Serial.println("Modo Master Ativo");
        
        if(mode == SLAVE_MODE)
            Serial.println("Modo Slave Ativo");

        if(mode == MISTER_MODE)
            Serial.println("Modo Misto Ativo");

        if(mode == MASTER_MODE || mode == MISTER_MODE)
            server.connect();
        
        if(mode == SLAVE_MODE || mode == MISTER_MODE)
            sensors.setup();
    }

    void handle(){
        if(mode == SLAVE_MODE  || mode == MISTER_MODE){
            sensors.handle();
        }

        if(mode == MASTER_MODE || mode == MISTER_MODE){
            server.handle();
            server.check();
        }
        
        if(mode == SLAVE_MODE){
            telemetry.handle();
            logs.handle();
        }
    }

    void reset(){
        ESP.restart();
    }
};


inline Device device;

void setup(){
    Serial.begin(115200);
    delay(800);
    setup();
}

void loop(){
    device.handle();
}
