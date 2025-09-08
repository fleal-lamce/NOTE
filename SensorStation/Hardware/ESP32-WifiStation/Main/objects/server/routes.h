#ifndef ROUTES_H
#define ROUTES_H
#include "../device/index.h"
#include "index.h"



class Routes{
  public:

    void handle(){
        if(!server.available)
            return;
        
        server.available = false;
        //Serial.println("request: " + server.request);

        if(server.requested("INFO"))
            server.send("Hi");

        if(server.requested("CHECK"))
            server.send("OK");
    }

};

inline Routes routes;
#endif