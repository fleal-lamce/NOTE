#ifndef ROUTES_H
#define ROUTES_H
#include <Arduino.h>


template <typename Parent> class Routes{
  private:
    Parent* device;

  public:
    Routes(Parent* dev):
        device(dev){}

    void handle(){
        if(!device->server.available)
            return;
        
        device->server.available = false;
        //Serial.println("request: " + device->server.request);

        if(device->server.requested("INFO"))
            device->server.send("Hi");

        if(device->server.requested("CHECK"))
            device->server.send("OK");
    }

};

#endif