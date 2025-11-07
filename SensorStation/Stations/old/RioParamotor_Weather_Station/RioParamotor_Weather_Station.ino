/*
 *  Escola Rio Paramotor Weather Station
 *  
 *  Send data to:
 *    - Windy.com
 *    - Thingspeak.com
 *    - Wunderground.com
 *    - Weathercloud.net
 *    - Pwsweather.com
 *    - Windguru.cz
 *  
 *  Main board: NodeMCU ESP12e 
 *  Anemometer: WRL Eletrônica
 *  Sensor board: GY-BME2080
 *  
 *  based on:
 *  https://www.instructables.com/id/NodeMCU-Wireless-Weather-Station/
 *  
 *  modified by: 
 *    ggcvirtual@gmail.com - jan2022
 */
 
#include <ESP8266WiFi.h> //https://github.com/esp8266/Arduino/archive/master.zip
#include <WiFiUdp.h>
#include <ESP8266WiFiMulti.h>
//#include "cactus_io_BME280_I2C.h" // http://static.cactus.io/downloads/library/bme280/cactus_io_BME280_I2C.zip
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>  //https://github.com/jandrassy/ArduinoOTA
#include <EEPROM.h>
#include <TimeLib.h>

ESP8266WiFiMulti wifiMulti;


//--------------------------------PWS  altitude ------------------------------------------
float altitudepws = 18.00;  //Local  altitude of the PWS to get relative pressure  meters (m)


//-------------------------------BME280----------------------------------------
//BME280_I2C bme(0x76);   // I2C using address 0x76
Adafruit_BME280 bme;      // I2C


//------------------------------Rain------------------------------------------------
//int RainSensorPin = D6;              //Rain REED-ILS sensor GPIO 12
//#define Bucket_Size_US 0.012         // rain bucket size inches 
//#define Bucket_Size_EU 0.3           // rain bucket size milimetres ( 0.3mm)


//float tipCount1h ;   // bucket tip counter used in interrupt routine
//float tipCount24h ;  // bucket tip counter used in interrupt routine  
//unsigned int counter = 15;
//volatile unsigned long contactTime;


//--------------------------------Wind  speed----------------------------------------
int WindSensorPin = D5;                    // Wind speed -ILS sensor (anemometer) GPIO 14
volatile unsigned long Rotations = 0;      // cup rotation counter used in interrupt routine
volatile unsigned long ContactBounceTime;  // Timer to avoid contact bounce in interrupt routine

const float pi = 3.14159265;     //Número de pi
unsigned long period = 1000;     //Tempo de medida(miliseconds)
int radius = 147;                //Raio do anemometro(mm)
//unsigned int scounter = 0;       //Contador para o sensor  
unsigned int RPM = 0;            //Rotações por minuto
float speedmps = 0;              //Velocidade do vento (m/s)
float speedkph = 0;              //Velocidade do vento (km/h)
float speedmph = 0;              //Velocidade do vento (milhas/h)
float speedknots = 0;            //Velocidade do vento (knots)


//-------------------------------Wind direction-----------------------------------------------
float wind_avg;         // average wind direction
int vane_value;         // raw analog value from wind vane
int Direction;          // translated 0 - 360 direction
int CalDirection;       // converted value with offset applied
#define Offset 0;
int windDirections[] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
 


//--------------------------------Setup Wifi----------------------------------------------
const char* ssid1     = "GGCWiFi-V";   //I use multiple SSID In my home, but you can only define one.
const char* password1 = "abcdef1234";

const char* ssid2     = "xxxxxxx";
const char* password2 = "xxxxxxx";

const char* ssid3     = "xxxxxxxxx";
const char* password3 = "xxxxxxxxx";

const int sleepTimeS = 300; //18000 for Half hour, 300 for 5 minutes etc.


//----------------------------------------------------------------------------------------
WiFiUDP Udp;
unsigned int localPort = 8888;  // local port to listen for UDP packets


time_t getNtpTime();
void digitalClockDisplay();
void printDigits(int digits);
void sendNTPpacket(IPAddress &address);

unsigned long initTimer1;
unsigned long initTimer2;


//--------------------------------WEATHER VAR---------------------------------------------
float temp2c;               // Temp celsius  BME280
float temp2c_min = 100;     // Minimum temperature C
float humidity2;            // Humidity BME280
float temp_f;               // Temp farenheit 
float dewpt_f;              // dew point (F)
float dewpt_c;              // dew point (C)
float heat_f;               // heat index (F)
float heat_c;               // heat index (C)
float windSpeed = 0;        // Wind speed (mph)
float wind_speed_min = 100; // Minimum wind speed (mph)
float wind_speed_avg;       // 10 minutes average wind speed ( mph)
float windgustmph = 0;      // Wind gust speed( mph)
float windmax = 0;
float barompa;              // Preasure pascal Pa
float last_baromhpa;        // previous preasure value
float baromin;              // Preasure inches of mercury InHg
float baromhpa;             // Preasure hectopascal hPa
//float rain1h = 0;         // Rain inches over the past hour
//float rain = 0;           // Rain milimetres over the past hour
//float rain24h = 0;        // Rain inches over the past 24 hours
//float rainrate = 0;       // Rain milimetres over the past 24 hours
float chill_f;              // Windchill (F)
float chill_c;              // Windchill (C)
int dBm;                    // WiFi signal strenght dBm
int quality;                // WiFi signal quality %
int chk;
//String eepromstring = "0.00";

int rmin = 1000; 
int rmax = 0;
int Winddir = 0;                 //Direção do vento em graus
String WindN = "N ";             //Direção do vento em quadrante 

int counter = 0;
bool debug = 1;           //debug = 1 -> enable debug
int LED_pin = 16;

int delay1 = 10000;       // 10s delay para enviar dados ao Thingspeak
int delay2 = 60000;       // 60s delay para enviar dados aos outros sites
int delay3 = 300000;      // 3min delay para calcular rajadas e velocidade média


//-------------------------------- Interruption Functions ---------------------------------------------
//void ICACHE_RAM_ATTR isr_rg();          //rain 
void ICACHE_RAM_ATTR isr_rotation();      //rotation
void ICACHE_RAM_ATTR funcaoInterrupcao(); //rotation


//-------------------------------------------------------------------------------------------------------------
////////////////////////////////////MAIN PROGRAM START/////////////////////////////////////////////////////////
//-------------------------------------------------------------------------------------------------------------
void setup()
{
  pinMode(LED_pin, OUTPUT);     // Initialize the LED_BUILTIN pin as an output

  Serial.begin(115200);

  Serial.println();
  Serial.println("-----------------------------------------------------");
  Serial.println(" RioParamotor Weather Station  v0.1");
  Serial.println(" Gerson Cunha jan 2022");
  Serial.println("-----------------------------------------------------");
  Serial.println("Starting... ");
  Serial.println();
  
  digitalWrite(LED_pin, LOW);   // Turn the LED on (Note that LOW is the voltage level
  delay(2000);

  Start_BME280();      //inicializa sensor de temperatura, humidade e pressão
  
  //StartEPROM();

  Start_Wifi();          // inicializa wifi

  Start_Ntp();           // inicializa ntp (time server)
    
  //pinMode(RainSensorPin, INPUT);
  //attachInterrupt(digitalPinToInterrupt(RainSensorPin), isr_rg, FALLING);  
  
  pinMode(WindSensorPin, INPUT);
  //attachInterrupt(digitalPinToInterrupt(WindSensorPin), isr_rotation, FALLING);  // change if low to high >> RISING
  attachInterrupt(digitalPinToInterrupt(WindSensorPin), funcaoInterrupcao, RISING);
  //attachInterrupt(digitalPinToInterrupt(WindSensorPin), isr_rotation, RISING);
  sei();

  // reprogramação via wifi - OTA : Over-The-Air
  Start_ArduinoOTA();

  // temporizador do upload
  initTimer1 = millis();
  initTimer2 = millis();

  Serial.println();
  Serial.println("Collecting data from sensors...");
  Serial.println();
  
  digitalWrite(LED_pin, HIGH);  // Turn the LED off by making the voltage HIGH
}
time_t prevDisplay = 0; // when the digital clock was displayed



//-------------------------------------------------------------------------------------------------------------
void loop()
{

  Serial.print(" Local Time: ");
  Serial.print(hour()-3);      // corrigido fuso utm - 3
  printDigits(minute());
  printDigits(second());
  Serial.print("  - next upload in  ");
  Serial.print(int(float(delay1 - (millis() - initTimer1)) /1000.0F));   // tempo para enviar thingspeak
  Serial.print(" seg and  ");
  Serial.print(int(float(delay2 - (millis() - initTimer2)) /1000.0F));   // tempo para enviar aos sites
  Serial.println(" seg");

  //Start_BME280();      //inicializa sensor de temperatura, humidade e pressão
  read_BME280();             // read sensors data from analog and digital pins of ESP8266
  
  //getWindSpeed();
  //isr_rotation();
  getWindSpeedNEW();
  
  //getWindDirection();
  getWindDirectionNEW();

  get_RSSIdBm();               // WiFi signal quality (RSSI)
  
  Serial.println();

  // envia dados a cada 10 seg
  if( millis() > initTimer1 + delay1 ) 
  {
    digitalWrite(LED_pin, LOW);   // Turn the LED on (Note that LOW is the voltage level
    Serial.println("-----------------------------------------------------");
    thingspeak();            // sends data to thingspeak.com

    initTimer1 = millis();
    digitalWrite(LED_pin, HIGH);  // Turn the LED off by making the voltage HIGH
  } 

  // envia dados a cada 60 seg
   if( millis() > initTimer2 + delay2 )
  {
    digitalWrite(LED_pin, LOW);   // Turn the LED on (Note that LOW is the voltage level
    Serial.println("-----------------------------------------------------");
    wunderground();          // sends data to wunderground.com
    weathercloud();          // sends data to weathercloud.net
    windy();                 // sends data to windy.com
    pws();                   // sends data to pwsweather.com
    windguru();              // sends data to windguru.cz

    initTimer2 = millis();
    digitalWrite(LED_pin, HIGH);  // Turn the LED off by making the voltage HIGH
   } 
  
  // reset no calculo da velocidade média e rajadasa a cada 5 min 
  if( millis() > initTimer2 + delay3 )
  {
    Serial.println("####### reset 5 min #######");
    windgustmph = 0;
    wind_speed_avg = 0;
    wind_speed_min = 100;
  }
  
  //time_ntp();              // get time from NTP server

  //Gravação Over-The-Air (OTA)
  ArduinoOTA.handle();
}




//------------------------------------------------------------------------------------------------------------
/////////////////////////////////////////////// Counter /////////////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------
void Counter()
{
  if (counter == 18)
  {
    windgustmph = 0;
    wind_speed_avg = 0;
    wind_speed_min = 100;
    temp2c_min = 100;
    counter = 0;  //10 minutes loop     30*20=600s = 10min
  }
  counter++;
}



//------------------------------------------------------------------------------------------------------------
/////////////////////////////////////////////// ESP8266 sleep mode ///////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------
void sleepMode() {
  Serial.print(F("Sleeping..."));
  ESP.deepSleep(sleepTimeS * 1000000);
}
