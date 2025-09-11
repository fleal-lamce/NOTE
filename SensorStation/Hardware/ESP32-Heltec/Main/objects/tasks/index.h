#ifndef TASKS_H
#define TASKS_H
#include <Arduino.h>
#include "../../globals/constants.h"
#include "../../globals/functions.h"
#include "../../utils/listener/index.h"
#include "../device/index.h"


class Tasks{
  public:
    void handle(){
        if(device.mode == SLAVE_MODE  || device.mode == MISTER_MODE)
            device.sensors.handle();

        if(device.mode == MASTER_MODE || device.mode == MISTER_MODE)
            master();
        
        if(device.mode == SLAVE_MODE)
            slave();

        standard();
    }

    void master(){
        device.server.handle();
        device.server.check();
    }

    void slave(){
        
    }

    void standard(){
        device.telemetry.handle();
        device.logs.handle();
    }
};

inline Tasks tasks;
#endif
