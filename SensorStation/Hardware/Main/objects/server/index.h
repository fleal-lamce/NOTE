#ifndef SERVER_H
#define SERVER_H
#include <WiFi.h>
#include <HTTPClient.h>
#include <esp_wifi.h>
#include "../../globals/constants.h"
#include "../../globals/variables.h"
#include "../../globals/functions.h"
#include "../device/index.h"
#include "../../utils/text/index.h"
#include "../../utils/listener/index.h"


class EspServer{
    public:
    bool available  = false;
    bool active     = false;
    const char* URL = "http://192.168.0.10:8000/api/";
    WiFiServer server{80};
    WiFiClient client;
    Text<512> request;

    void handle(){
        static Listener listener(50);

        if(!listener.ready() || !device.master)
            return;
        
        client = server.available();

        if(!client)
            return;

        request.reset();

        while(client.available())
            request.append(client.read());
        
        available = (request.length() > 2);
    }

    void check(){
        static Listener listener(30000);
        
        if(!listener.ready() || !device.master)
            return;
        
        Text<32> response;
        response.concat(get("check/")); 

        active = response.contains("OK");
        Serial.println("server status: " + String(active));
    }

    bool requested(const char* route){
        const char* prefix = concatenate("GET /", route);
        return request.contains(prefix);
    }

    bool connected(){
        return (WiFi.status() == WL_CONNECTED);
    }

    void send(const String& data) {
        client.print(
            "HTTP/1.1 200 OK\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Content-Type: text/plain\r\n"
            "Connection: close\r\n"
            "\r\n"
        );

        client.print(data);
    }

    String post(const String &route, const String &data) {
        if(!connected())
            return "-1";

        HTTPClient http;
        http.begin(String(URL) + route);
        http.addHeader("Content-Type", "application/json");
        http.setTimeout(5000);

        int code = http.POST(data);
        int size = http.getSize();
        bool ok = (code > 0 && size < 2048);
        String payload = ok ? http.getString() : "-1";

        http.end();
        return payload;
    }

    String get(const String &route){
        if(!connected())
            return "-1";
        
        HTTPClient http;
        http.begin(String(URL) + route);
        http.setTimeout(5000);

        int code = http.GET();
        String payload = (code > 0) ? http.getString() : "-1";
        
        http.end();
        return payload;
    }

    void connect(const char* ssid, const char* pass){
        unsigned long startTime = device.time();
        WiFi.mode(WIFI_STA);

        esp_wifi_set_protocol(WIFI_IF_STA, WIFI_PROTOCOL_11B | WIFI_PROTOCOL_11G | WIFI_PROTOCOL_11N);
        esp_wifi_set_bandwidth(WIFI_IF_STA, WIFI_BW_HT20);
        esp_wifi_set_ps(WIFI_PS_NONE);
        WiFi.setTxPower(WIFI_POWER_19_5dBm);
        WiFi.begin(ssid, pass);

        while(device.time() - startTime < 5000){
            if(!connected()){
                delay(100);
                continue;
            }
            
            Serial.print("Conectado! IP do ESP32: ");
            Serial.println(WiFi.localIP());
            break;
        }

        if(!connected()){
            Serial.print("Falha ao conectar no Wi-Fi");
            Serial.println();
        }

        server.begin();
    }
};


inline EspServer server;
#endif