#include "globals/constants.h"
#include "globals/functions.h"
#include "objects/device/index.h"
#include "objects/tasks/index.h"
#include "objects/server/index.h"
#include "objects/server/routes.h"
#include "objects/logs/index.h"
#include "objects/sensors/index.h"
#include "objects/wireless/heltec/index.h"
#include "objects/telemetry/protocol/index.h"
#include "objects/telemetry/multiplexer/index.h"


void setup(){
    Serial.begin(115200);
    delay(800);
    
    device.setup();
    heltec.setup();

    if(device.master){
        logs.setup();
        server.connect();
    }
    
    if(!device.master){
        multiplexer.setup();
        sensors.setup();
        multiplexer.setup();
    }
}

void loop(){
    device.master ? tasks.master() : tasks.slave();
    tasks.standard();
}
