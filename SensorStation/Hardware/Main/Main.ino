#include "globals/constants.h"
#include "globals/variables.h"
#include "globals/functions.h"
#include "objects/device/index.h"
#include "objects/tasks/index.h"
#include "objects/server/index.h"
#include "objects/server/routes.h"
#include "objects/logs/index.h"
#include "objects/sensors/index.h"
#include "objects/telemetry/heltec/index.h"


void setup(){
    Serial.begin(115200);
    delay(2000);
    device.setup(); 
    heltec.setup();
    
    if(device.master){
        server.connect("Klauss", "Marchi12345@");
        logs.setup();
        return;
    }
    
    sensors.setup();
}

void loop(){
    logs.handle();

    if(device.master)
        tasks.master();
    else
        tasks.slave();
}
