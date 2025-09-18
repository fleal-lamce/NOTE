#include "objects/device/index.h"
#include "objects/tasks/index.h"
// NOTE V0.1.0

void setup(){
    Serial.begin(115200);
    delay(800);
    device.setup();
}

void loop(){
    tasks.handle();
}
