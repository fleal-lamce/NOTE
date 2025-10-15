#ifndef QML201C_H
#define QML201C_H
#include <Arduino.h>
#include "../../../../utils/text/index.h"
#include "../../../../utils/listener/index.h"
#define RX_PIN 19
#define TX_PIN 20


template <typename Parent> class QML201C{
  private:
    Parent* device;

  public:
    QML201C(Parent* dev):
        device(dev){}  
    
    void setup(){
        Serial.println("QML Telemetry Started");
        return;
        Serial2.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);
        device->telemetry.serial.timeout = 5000;
        device->telemetry.serial.await(700);
        
        device->telemetry.serial.send("open");
        device->telemetry.serial.await(2500);
        device->telemetry.serial.print();

        device->telemetry.serial.send("help lastval");
        device->telemetry.serial.await(3000);
        device->telemetry.serial.print();

        device->telemetry.serial.send("rep MyRep0");
        device->telemetry.serial.await(3000);
        device->telemetry.serial.print();

        device->telemetry.serial.send("logstatus");
        device->telemetry.serial.await(2500);
        device->telemetry.serial.print();
    }

    void handle(){
        static Listener listener = Listener(12000);
        
        if(!listener.ready())
            return;

        return;

        query("LASTVAL TAMeasQMH101_1 status");
        query("LASTVAL TAMeasQMH101_1 TA");
        query("LASTVAL TAMeasQMH101_1 unconv");
    }

    void query(const char* cmd){
        device->telemetry.serial.send(cmd);
        device->telemetry.serial.await(2000);
        device->telemetry.serial.print();
    }

    void check(){
        if(!device->telemetry.serial.available)
            return;
        
        if(device->telemetry.serial.command.length() > 100)
            return;

        if(device->telemetry.serial.command.contains("QMLCHECK")){
            device->telemetry.response.set("$ETATACK!");
            return;
        }
    }
};


#endif