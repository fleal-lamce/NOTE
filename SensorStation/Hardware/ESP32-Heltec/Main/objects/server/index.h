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
        check();

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
        static Listener timer = Listener(10000);
        
        if(!timer.ready())
            return;
        
        Text<64> response = get("api/check/", 12000);
        active = response.contains("success");
        Serial.println("server status: " + String(active));
        
        if(!active)
            WiFi.reconnect();
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
        client.flush();
        client.stop();
    }

    String post(const String &route, const String &data, const int timeout=7000){
        if(!connected())
            return "-1";

        const String url = URL.toString() + route;
        HTTPClient http;

        http.begin(url);
        http.addHeader("Content-Type", "application/json");
        http.setTimeout(timeout);
        
        const int code = http.POST(data);
        const bool success   = (code >= 200 && code < 300);
        const String payload = success ? http.getString() : "-1";

        if(!success)
            Serial.println(url + " | http error code: " + String(code));

        http.end();
        return payload;
    }

    String get(const String &route, const int timeout=7000){
        if(!connected())
            return "-1";
        
        const String url = URL.toString() + route;
        HTTPClient http;

        http.begin(url);
        http.setTimeout(timeout);

        const int code = http.GET();
        const bool success   = (code >= 200 && code < 300);
        const String payload = success ? http.getString() : "-1";

        if(!success)
            Serial.println(url + " | http error code: " + String(code));
        
        http.end();
        return payload;
    }

    void connect(const int timeout=5000){
        const char* ssid = device->settings.template get<const char*>("ssid");
        const char* pass = device->settings.template get<const char*>("pass");
        
        URL = device->settings.template get<const char*>("server");
        const unsigned long startTime = Time::get();
        WiFi.mode(WIFI_STA);
        esp_wifi_set_ps(WIFI_PS_NONE);
        WiFi.begin(ssid, pass);

        while(Time::get() - startTime < timeout){
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