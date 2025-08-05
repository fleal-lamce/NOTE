#ifndef MULTIPLEXER_H
#define MULTIPLEXER_H
#include <Arduino.h>
#include "../../device/index.h"
#include "../../../utils/text/index.h"
#include "../../../utils/listener/index.h"
#include "../../serial/index.h"
#define TX_PIN 33
#define RX_PIN 26


class Multiplexer{
  public:
    NextSerial<1024> serial = NextSerial<1024>(Serial2);

    void setup(){
        Serial2.begin(115200, SERIAL_8N1, TX_PIN, RX_PIN);
        serial.timeout = 5000;
    }

    void handle(){
        static Listener listener = Listener(100);
        serial.listen();

        if(listener.ready())
            return;

        if(!serial.available)
            return;

        auto response = serial.command;
        Serial.println("multiplexer response: " + response.toString());
    }
};

inline Multiplexer multiplexer;
#endif