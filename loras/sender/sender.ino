#include "LoRaWan_APP.h"
#define RF_FREQUENCY           915000000 // Hz
#define TX_OUTPUT_POWER        14        // dBm
#define LORA_BANDWIDTH         0         // 125 kHz
#define LORA_SPREADING_FACTOR  7         // SF7
#define LORA_CODINGRATE        1         // 4/5
#define LORA_PREAMBLE_LENGTH   8
#define TX_TIMEOUT_MS          2000      // tempo máximo para esperar TxDone

// board:   https://resource.heltec.cn/download/package_heltec_esp32_index.json
// library: heltec esp32 dev-boards, adafruit gfx
// select: wifi lora v3

struct __attribute__((packed)) SensorData {
    char device_id[12];
    int area_id;
    int temperature;  
    int humidity;
    int pressure;  
    int battery;
};

class HeltecLora {
    public:
    volatile bool available = false;
    static RadioEvents_t radioEvents;
    static HeltecLora*  instance;
    SensorData txData;
    SensorData rxData;
    bool radioIdle = true;

    void setup() {
        instance = this;
        Mcu.begin(HELTEC_BOARD, SLOW_CLK_TPYE);
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

    bool send(const SensorData& data, uint32_t timeoutMs = TX_TIMEOUT_MS) {
        if(!radioIdle)
            return false;

        memcpy(&txData, &data, sizeof(txData));
        radioIdle = false;
        Radio.Send((uint8_t*)&txData, sizeof(txData));
        
        uint32_t start = millis();
        while(!radioIdle && (millis() - start < timeoutMs))
            Radio.IrqProcess();

        if(radioIdle)
            return true;

        radioIdle = true;
        return false;
    }

    bool get(SensorData& output) {
        Radio.IrqProcess();
        
        if(!available)
            return false;
        
        available = false; 
        memcpy(&output, &rxData, sizeof(rxData));
        return true;
    }

    static void onReceive(uint8_t* payload, uint16_t size, int16_t rssi, int8_t snr) {
        if(size == sizeof(SensorData)){
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

void setup() {
    Serial.begin(115200);
    heltec.setup();
}

void loop(){
    static SensorData data;
    strncpy(data.device_id, "NODE_1234", sizeof(data.device_id));
    data.area_id    = 12;
    data.temperature = millis();
    data.humidity    = 500;
    data.pressure    = 1013; 
    data.battery     = 3700; 

    heltec.send(data);
    delay(5000);
}
