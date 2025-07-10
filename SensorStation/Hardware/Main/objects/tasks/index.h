#ifndef TASKS_H
#define TASKS_H
#include <Arduino.h>
#include "../../globals/constants.h"
#include "../../globals/variables.h"
#include "../../globals/functions.h"
#include "../device/settings.h"
#include "../utils/text/index.h"
#include "../utils/json/index.h"
#include "../device/index.h"
#include "../utils/listener/index.h"


class Tasks{
    public:

    void print(){
        static Listener listener(5000);
        
        if(!listener.ready())
            return;
        
    }
};

inline Tasks tasks;
#endif