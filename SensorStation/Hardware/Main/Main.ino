#include "globals/constants.h"
#include "globals/functions.h"
#include "objects/device/index.h"
#include "objects/tasks/index.h"
#include "objects/server/index.h"
#include "objects/server/routes.h"
#include "objects/logs/index.h"
#include "objects/sensors/index.h"
#include "objects/telemetry/protocol/index.h"
#include "objects/telemetry/multiplexer/index.h"
//#include "objects/wireless/heltec/index.h"

void setup(){
    Serial.begin(115200);
    delay(800);

    device.setup();

    //if(device.mode != MISTER_MODE)
        //heltec.setup();

    if(device.mode == MASTER_MODE || device.mode == MISTER_MODE){
        logs.setup();
        server.connect();
    }
    
    if(device.mode == SLAVE_MODE || device.mode == MISTER_MODE){
        sensors.setup();
    }

    if(device.mode == SLAVE_MODE){
        multiplexer.setup();
    }

    Serial.println("setup finished");
}

void loop(){
    tasks.handle();
}
