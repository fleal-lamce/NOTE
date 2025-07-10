#include "globals/constants.h"
#include "globals/variables.h"
#include "globals/functions.h"
#include "objects/device/index.h"
#include "objects/tasks/index.h"
#include "objects/server/index.h"
#include "objects/server/routes.h"
#include "objects/logs/index.h"
#include "objects/sensors/index.h"
#include "objects/utils/notes/index.h"
#include "objects/telemetry/lora/index.h"
#include "objects/telemetry/espnow/index.h"


void setup(){
    Serial.begin(115200);
    device.setup();
    server.connect("Klauss", "Marchi12345@");
    device.islora ? lora.setup() : espnow.setup();
    sensors.setup();
    Serial.println("Setup Complete");
}

void loop(){
    tasks.print();
    server.handle();
    server.check();
    routes.handle();
    sensors.handle();
    routes.handle();
    logs.handle();
}

