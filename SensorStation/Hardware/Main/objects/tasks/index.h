#ifndef TASKS_H
#define TASKS_H
#include <Arduino.h>
#include "../../globals/constants.h"
#include "../../globals/functions.h"
#include "../../utils/listener/index.h"
#include "../device/index.h"
#include "../server/index.h"
#include "../server/routes.h"
#include "../logs/index.h"
#include "../sensors/index.h"
#include "../telemetry/protocol/index.h"
#include "../telemetry/multiplexer/index.h"


class Tasks{
  public:

    void handle(){
        if(device.mode == SLAVE_MODE  || device.mode == MISTER_MODE)
            sensors.handle();

        if(device.mode == MASTER_MODE || device.mode == MISTER_MODE)
            master();
        
        if(device.mode == SLAVE_MODE)
            slave();

        standard();
    }

    void master(){
        server.handle();
        server.check();
        routes.handle();
    }

    void slave(){
        multiplexer.handle();
    }

    void standard(){
        protocol.handle();
        logs.handle();
    }
};

inline Tasks tasks;
#endif
