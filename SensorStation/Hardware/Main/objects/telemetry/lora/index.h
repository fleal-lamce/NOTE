#ifndef ESPLORA_H
#define ESPLORA_H
#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include "../../../globals/constants.h"
#include "../../../globals/variables.h"
#include "../../../globals/functions.h"

// ———————————————————— CONFIGURAÇÃO LORA ————————————————————
#define LORA_SCK      5
#define LORA_MISO     19
#define LORA_MOSI     27
#define LORA_SS       18
#define LORA_RST      14
#define LORA_DIO0     26

#define LORA_FREQ     868000000UL
#define LORA_SF       12
#define LORA_BW       125E3
#define LORA_CR       7
#define LORA_PREAMBLE 8
#define LORA_SYNC     0x12
#define LORA_POWER    22
#define LORA_CRC      false


class EspLora{
    public:
    bool working = false;
    int  rssi = 0;

    void setup(){
        SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI);
        LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

        if(!begin(LORA_FREQ)){
            Serial.println("LoRa init failed");
            return;
        }

        LoRa.setSpreadingFactor(LORA_SF);
        LoRa.setSignalBandwidth(LORA_BW);
        LoRa.setCodingRate4(LORA_CR);
        LoRa.setPreambleLength(LORA_PREAMBLE);
        
        (LORA_CRC) ? LoRa.enableCrc() : LoRa.disableCrc();
        LoRa.setSyncWord(LORA_SYNC);
        LoRa.setTxPower(LORA_POWER);
        working = true;
    }

    bool send(DeviceData& data){
        LoRa.beginPacket();
        LoRa.write(reinterpret_cast<const uint8_t*>(&data), sizeof(data));
        int sent = LoRa.endPacket();
        return (sent > 0);
    }
    
    bool get(DeviceData& data){
        if(LoRa.parsePacket() != (int) sizeof(data)) 
            return false;
        
        LoRa.readBytes(reinterpret_cast<uint8_t*>(&data), sizeof(data));
        rssi = LoRa.packetRssi();
        return true;
    }
};

inline EspLora lora;
#endif
