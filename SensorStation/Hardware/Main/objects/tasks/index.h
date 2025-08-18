#ifndef TASKS_H
#define TASKS_H
#include <Arduino.h>
#include "../../globals/constants.h"
#include "../../globals/functions.h"
#include "../../utils/listener/index.h"
#include "../server/index.h"
#include "../server/routes.h"
#include "../logs/index.h"
#include "../sensors/index.h"
#include "../telemetry/protocol/index.h"
#include "../telemetry/multiplexer/index.h"


class Tasks{
  public:

    void master(){
        server.handle();
        server.check();
        routes.handle();
    }

    void slave(){
        sensors.handle();
        multiplexer.handle();
    }

    void standard(){
        protocol.handle();
        logs.handle();
    }

    void blink(){

    }
};

inline Tasks tasks;
#endif