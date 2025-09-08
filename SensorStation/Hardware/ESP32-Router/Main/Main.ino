#include <esp_wifi.h>
#include <WiFi.h>
#include <WebServer.h>


class Router{
  public:
    WebServer server{80};

    void setup(){
        esp_wifi_set_ps(WIFI_PS_NONE);
        WiFi.mode(WIFI_AP);
        WiFi.setTxPower(WIFI_POWER_19_5dBm);

        const char* serverName = "SensorStation";
        const char* serverPass = "12345678";
        const int channel = 1;  
        setRouter(serverName, serverPass, channel);
        setRoutes();
        server.begin();
    }

    void setRouter(const char* ssid, const char* pass, int channel){
        IPAddress staticIP(192, 168, 4, 2);   // IP ESTÁTICO
        IPAddress gateway(192, 168, 4, 2);    // GATEWAY ESTÁTICO IP
        IPAddress subnet(255, 255, 255, 0);

        WiFi.softAPConfig(staticIP, gateway, subnet);
        delay(100);

        WiFi.softAP(ssid, pass, channel);
        delay(100);

        Serial.print("SERVER STARTED: ");
        Serial.println(WiFi.softAPIP());
        Serial.println("Channel: " + String(channel));
        Serial.println();
    }

    void setRoutes(){
        server.on("/CHECK", HTTP_GET, [this]() {
            this->onCheckRequest();
        });
    }

    void onCheckRequest(){
        server.sendHeader("Access-Control-Allow-Origin", "*");
        server.send(200, "text/plain", "OK");
    }
};


Router router;

void setup(){
    Serial.begin(115200);
    delay(1000); Serial.println();
    router.setup();
    Serial.println("Router Started");
}

void loop(){
    router.server.handleClient();
}
