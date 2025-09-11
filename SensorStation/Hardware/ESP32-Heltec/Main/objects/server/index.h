#ifndef SERVER_H
#define SERVER_H
#include <WiFi.h>
#include <HTTPClient.h>
#include <esp_wifi.h>
#include "../../globals/constants.h"
#include "../../globals/functions.h"
#include "../../utils/text/index.h"
#include "../../utils/listener/index.h"
#include "../../utils/time/index.h"
#include "routes/index.h"


template <typename Parent> class EspServer{
  private:
    WiFiServer server = WiFiServer(80);
    WiFiClient client = WiFiClient();
    Parent* device;
    Routes<Parent> routes;
  
  public:
    bool available = false;
    bool active    = false;
    Text<64>  URL;
    Text<512> request;

    EspServer(Parent* dev):
        device(dev),
        routes(dev){}

    void handle(){
        static Listener listener = Listener(50);

        if(!listener.ready())
            return;
        
        client = server.available();

        if(!client)
            return;

        request.reset();

        while(client.available())
            request.append(client.read());
        
        available = (request.length() > 2);
        routes.handle();
    }

    void check(){
        static Listener listener = Listener(30000);
        
        if(!listener.ready())
            return;
        
        Text<64> response = get("check/", 12000);
        Serial.println(response.toString());

        active = response.contains("success");
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

    String post(const String &route, const String &data, const int timeout=5000){
        if(!connected())
            return "-1";

        HTTPClient http;
        http.begin(URL.toString() + route);
        http.addHeader("Content-Type", "application/json");
        http.setTimeout(timeout);

        int code = http.POST(data);
        int size = http.getSize();
        bool ok = (code > 0 && size < 2048);
        String payload = ok ? http.getString() : "-1";

        http.end();
        Serial.println("(post) size: " + String(size) + " | received: " + payload);
        return payload;
    }

    String get(const String &route, const int timeout=5000){
        if(!connected())
            return "-1";
        
        HTTPClient http;
        http.begin(URL.toString() + route);
        http.setTimeout(timeout);

        int code = http.GET();
        String payload = (code > 0) ? http.getString() : "-1";
        
        http.end();
        return payload;
    }

    void connect(){
        const char* ssid = device->settings.template get<const char*>("ssid");
        const char* pass = device->settings.template get<const char*>("pass");

        URL = device->settings.template get<const char*>("server");
        const unsigned long startTime = Time::get();
        WiFi.mode(WIFI_AP_STA);
        
        esp_wifi_set_protocol(WIFI_IF_STA, WIFI_PROTOCOL_11B | WIFI_PROTOCOL_11G | WIFI_PROTOCOL_11N);
        esp_wifi_set_bandwidth(WIFI_IF_STA, WIFI_BW_HT20);
        esp_wifi_set_ps(WIFI_PS_NONE);
        WiFi.setTxPower(WIFI_POWER_19_5dBm);
        WiFi.begin(ssid, pass);

        while(Time::get() - startTime < 5000){
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

#endif