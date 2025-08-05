#ifndef ESPNOW_H
#define ESPNOW_H

#include <Arduino.h>
#include <esp_now.h>
#include <WiFi.h>
#include "../../../globals/dataset/index.h"
#include "../../device/index.h"


void onEspSend(const uint8_t *mac_addr, esp_now_send_status_t status);
void onEspReceive(const uint8_t *mac, const uint8_t *incomingData, int len);


class EspNow {
  public:
    uint8_t target_address[6];
    bool available = false;
    DeviceData receivedData;

    EspNow(){
        const uint8_t master_address[6] = {0x64, 0xB7, 0x08, 0x11, 0x35, 0x10};
        const uint8_t slave_address[6]  = {0xEC, 0x62, 0x60, 0xE0, 0xA7, 0x5C};
        memcpy(target_address, device.master ? slave_address : master_address, sizeof(target_address));
    }
    
    void setup(){
        if(esp_now_init() != ESP_OK){
            Serial.println("Erro ao iniciar ESP-NOW");
            return;
        }

        esp_now_register_send_cb(onEspSend);
        esp_now_register_recv_cb(onEspReceive);

        esp_now_peer_info_t peerInfo = {};
        memcpy(peerInfo.peer_addr, target_address, 6);
        peerInfo.channel = 0;
        peerInfo.encrypt = false;

        if(!esp_now_add_peer(&peerInfo))
            Serial.println("Peer adicionado com sucesso.");

        print();
    }

    void print(){ // formato "24:6F:28:3A:8C:B1"
        String mac = WiFi.macAddress(); 
        Serial.print("MAC Address: ");
        Serial.println(mac);
    }

    bool send(const DeviceData &data) {
        esp_err_t result = esp_now_send(target_address, (const uint8_t *)&data, sizeof(data));
        return (result == ESP_OK);
    }

    bool get(DeviceData &data) {
        if(!available) 
            return false;
        
        data = receivedData;
        available = false;
        return true;
    }

    void markReceived(const DeviceData &data){
        receivedData = data;
        available = true;
    }
};

inline EspNow espnow;

void onEspSend(const uint8_t *mac_addr, esp_now_send_status_t status){
    const bool success = (status == ESP_NOW_SEND_SUCCESS);
    return;
}

void onEspReceive(const uint8_t *mac, const uint8_t *incomingData, int len) {
    if(len == sizeof(DeviceData)){
        DeviceData temp;
        memcpy(&temp, incomingData, sizeof(DeviceData));
        espnow.markReceived(temp);
        return;
    } 

    //Serial.println("Dados com tamanho inválido.");
}

#endif