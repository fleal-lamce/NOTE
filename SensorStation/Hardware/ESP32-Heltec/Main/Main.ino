#include "objects/device/index.h"
#include "objects/tasks/index.h"


void setup(){
    Serial.begin(115200);
    delay(800);
    device.setup();
}

void loop(){
    tasks.handle();
}
