#ifndef MULTIPLEXER_H
#define MULTIPLEXER_H
#include <Arduino.h>
#include "../../device/index.h"
#include "../../../utils/text/index.h"
#include "../../../utils/listener/index.h"
#include "../../serial/index.h"

#define RX_PIN 19
#define TX_PIN 20


class Multiplexer{
  public:
    NextSerial<1024> serial = NextSerial<1024>(Serial2);

    void setup(){
        Serial2.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);
        serial.timeout = 5000;
        serial.await(700);
        
        serial.send("open");
        serial.await(2500);
        serial.print();

        serial.send("help lastval");
        serial.await(3000);
        serial.print();

        serial.send("rep MyRep0");
        serial.await(3000);
        serial.print();

        serial.send("logstatus");
        serial.await(2500);
        serial.print();
    }

    void handle(){
        static Listener listener = Listener(12000);
        
        if(!listener.ready())
            return;

        query("LASTVAL TAMeasQMH101_1 status");
        query("LASTVAL TAMeasQMH101_1 TA");
        query("LASTVAL TAMeasQMH101_1 unconv");
    }

    void query(const char* cmd){
        serial.send(cmd);
        serial.await(2000);
        serial.print();
    }
};

inline Multiplexer multiplexer;
#endif