#ifndef SERVER_LOGS_H
#define SERVER_LOGS_H
#include "../dataset/index.h"
//#include "../wireless/heltec/index.h"


template <typename Parent> class Logs{
  private:
    //HeltecLora heltec;
    Parent* device;
    
  public:
    Logs(Parent* dev):
        device(dev){}
    
    void setup(){
        //heltec.setup();
        delay(2000);
    }

    void handle(){
        if(device->sending)
            handleSender();
        
        if(device->serving)
            handleServer();
    }

    void handleSender(){
        static Listener timer = Listener(1*60*1000);
        
        if(!timer.ready())
            return;

        if(!device->sensors.available)
            return;
        
        //heltec.send(dataset.info); 
        device->sensors.available = false;
        Serial.println("(log) sent: " + dataset.toString());
    }

    void handleServer(){
        static Listener timer = Listener(30*1000);
        
        if(!timer.ready())
            return;

        if(!device->server.active)
            return;
        
        String log    = dataset.toString();
        String result = device->server.post("api/add_log/", log);
        Serial.println("(server) log:      " + log);
        Serial.println("(server) response: " + result);
        Serial.println();
    }
};

#endif