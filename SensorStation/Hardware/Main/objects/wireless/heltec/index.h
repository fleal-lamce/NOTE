#ifndef HELTEC_H
#define HELTEC_H
#include "../../../globals/dataset/index.h"
#include "../../device/index.h"
#include "LoRaWan_APP.h"

#define RF_FREQUENCY 915000000   // Hz
#define TX_OUTPUT_POWER 14       // dBm
#define LORA_BANDWIDTH  0        // 125 kHz
#define LORA_SPREADING_FACTOR 7  // SF7
#define LORA_CODINGRATE       1  // 4/5
#define LORA_PREAMBLE_LENGTH  8
#define TX_TIMEOUT_MS 2000 // tempo máximo para esperar TxDone

class HeltecLora{
  public:
    volatile bool available = false;
    static RadioEvents_t radioEvents;
    static HeltecLora*  instance;
    DeviceData txData;
    DeviceData rxData;
    bool radioIdle = true;

    void setup() {
        instance = this;
        //Mcu.begin(HELTEC_BOARD, SLOW_CLK_TPYE);
        radioEvents.RxDone     = onReceive;
        radioEvents.TxDone     = onTxComplete;
        radioEvents.TxTimeout  = onTxFailed;
        Radio.Init(&radioEvents);
        Radio.SetChannel(RF_FREQUENCY);

        Radio.SetRxConfig(
            MODEM_LORA, LORA_BANDWIDTH, LORA_SPREADING_FACTOR,
            LORA_CODINGRATE, 0, LORA_PREAMBLE_LENGTH, 0, 
            false, 0, true, 0, 0, false, true
        );
        
        Radio.SetTxConfig(
            MODEM_LORA, TX_OUTPUT_POWER, 0, LORA_BANDWIDTH, 
            LORA_SPREADING_FACTOR,  LORA_CODINGRATE, LORA_PREAMBLE_LENGTH, 
            false, true, 0, 0, false, TX_TIMEOUT_MS
        );

        Radio.Rx(0);
    }

    bool send(const DeviceData& data) {
        if(!radioIdle)
            return false;

        memcpy(&txData, &data, sizeof(txData));
        radioIdle = false;
        Radio.Send((uint8_t*)&txData, sizeof(txData));

        const unsigned long startTime = device.time();
        while(!radioIdle && (device.time() - startTime < TX_TIMEOUT_MS))
            Radio.IrqProcess();

        if(radioIdle)
            return true;

        radioIdle = true;
        return false;
    }

    bool get(DeviceData& output) {
        Radio.IrqProcess();
        
        if(!available)
            return false;
        
        available = false; 
        memcpy(&output, &rxData, sizeof(rxData));
        return true;
    }

    static void onReceive(uint8_t* payload, uint16_t size, int16_t rssi, int8_t snr) {
        if(size == sizeof(DeviceData)){
            memcpy(&instance->rxData, payload, size);
            instance->available = true;
        }

        Radio.Rx(0);
    }

    static void onTxComplete() {
        instance->radioIdle = true;
        Radio.Sleep();
    }

    static void onTxFailed() {
        instance->radioIdle = true;
        Radio.Sleep();
    }
};


HeltecLora*  HeltecLora::instance = nullptr;
RadioEvents_t HeltecLora::radioEvents;
inline HeltecLora heltec;
#endif