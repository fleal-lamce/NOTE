#include <MD5Builder.h>

MD5Builder _md5;     // Windguru API requires some MD5 hashing
String md5(String str) {
  _md5.begin();
  _md5.add(String(str));
  _md5.calculate();
  return _md5.toString();
}


//------------------------------------------------------------------------------------------------------------
///////////////////////////////// SEND DATA Configuration ////////////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------


//----------------------------Thingspeak.com  API Key ----------------------------------
const char* server1 = "api.thingspeak.com";
String Key1 ="N5WV3CXBCCFF4MA3";


//----------------------------Wunderground.com  ID PSW ----------------------------------
char server [] = "rtupdate.wunderground.com";
char ID [] = "IMARIC6";
char Key [] = "j6k9OZ5i";  

//----------------------------Weathercloud.net  ID Key ----------------------------------
const char* server2 = "api.weathercloud.net";
char ID2 [] = "3c337e4055733125";
char Key2 [] = "e38ec622d781434bbd2e8f1532384aad";  


//----------------------------Windy.com  API Key ----------------------------------
char server4 []  = "stations.windy.com";
char Key4 [] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaSI6MzU5NDY4MSwiaWF0IjoxNjQyNjUxNDAyfQ.ReukaPleT9OM_R6sNK9xZ9US7VhT23lMUdMeOFE6Bbs";


//----------------------------Pwsweather.com.  ID  ----------------------------------
char server5 [] = "pwsupdate.pwsweather.com";
char ID5 [] = "escolarioparamotor";
char Key5 [] = "b878bd61dd234cfbdca5356e0d34af1a";        


//----------------------------Windguru.com  ID  ----------------------------------
char server6 []  = "www.windguru.cz";
char ID6 [] = "escolarioparamotor";
char Key6 [] = "ggcvirtual2022";



//------------------------------------------------------------------------------------------------------------
/////////////////////////////////  SEND DATA TO  Thingspeak.com ////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------

void thingspeak(void)
{
  //if (counter == 17)
  //{
  //{  
    Serial.print("Connecting to ");
    Serial.print(server1);
    Serial.println("...");
    WiFiClient client;
    
    if (client.connect(server1, 80)) { // use ip 184.106.153.149 or api.thingspeak.com
      Serial.print("Connected to ");
      Serial.println(client.remoteIP());
  
      String postStr = Key1;
      postStr += "&field1=";
      postStr += String(temp2c_min);
      postStr += "&field2=";
      postStr += String(humidity2);
      postStr += "&field3=";
      postStr += String(baromhpa);
      postStr += "&field4=";
      //postStr += String(wind_speed_avg * 0.447);
      postStr += String(speedkph);
      postStr += "&field5=";
      postStr += String(speedknots);
      postStr += "&field6=";
      postStr += String(windgustmph * 0.447);
      //postStr += String(rain);
      postStr += "&field7=";
      postStr += String(Winddir);
      //postStr += String(getWindDirectionMax());
      postStr += "&field8=";
      postStr += String(quality);
      postStr += "\r\n\r\n";
   
      client.print("POST /update HTTP/1.1\n");
      client.print("Host: api.thingspeak.com\n");
      client.print("Connection: close\n");
      client.print("X-THINGSPEAKAPIKEY: " + Key1 + "\n");
      client.print("Content-Type: application/x-www-form-urlencoded\n");
      client.print("Content-Length: ");
      client.print(postStr.length());
      client.print("\n\n");
      client.print(postStr);
    
      Serial.println();
      delay(1000);
   
    }
    client.stop();
  //}
  //}
}


//------------------------------------------------------------------------------------------------------------
///////////////////////////////// SEND DATA TO Wunderground.com //////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------
void wunderground(void)
{
  Serial.print("Connecting to ");
  Serial.print(server);
  Serial.println("...");
  WiFiClient client;
  
  if (client.connect(server, 80)) {
    Serial.print("Connected to ");
    Serial.println(client.remoteIP());
    delay(100);
  } else {
    Serial.println("connection failed");
  }
  
  client.print("GET /weatherstation/updateweatherstation.php?");
  client.print("ID=");
  client.print(ID);
  client.print("&PASSWORD=");
  client.print(Key);
  client.print("&dateutc=now&winddir=");
  //client.print(CalDirection);
  client.print(Winddir);
  client.print("&tempf=");
  client.print(temp_f);
  client.print("&windspeedmph=");
  client.print(wind_speed_avg);    
  //client.print(speedkph / 1.609);    // convert kph to mph
  client.print("&windgustmph=");
  client.print(windgustmph);
  client.print("&dewptf=");
  client.print(dewpt_f);
  client.print("&humidity=");
  client.print(humidity2);
  client.print("&baromin=");
  client.print(baromin);
//  client.print("&rainin=");
//  client.print(rain1h);
//  client.print("&dailyrainin=");
//  client.print(rain24h);
  client.print("&softwaretype=NodeMCU-ESP12&action=updateraw&realtime=1&rtfreq=30");
  client.print("/ HTTP/1.1\r\nHost: rtupdate.wunderground.com:80\r\nConnection: close\r\n\r\n");
  
  Serial.println();
  delay(1000);
  
  //sleepMode();
}


//------------------------------------------------------------------------------------------------------------
/////////////////////////////////  SEND DATA TO  Weathercloud.net ////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------

void weathercloud(void)
{
//if (counter == 17){
//{
  Serial.print("Connecting to ");
  Serial.print(server2);
  Serial.println("...");
  
  WiFiClient client;
  if (client.connect(server2, 80)) {
    Serial.print("Connected to ");
    Serial.println(client.remoteIP());
  } else {
    Serial.println("connection failed");
  }
  
  client.print("GET /set/wid/");
  client.print(ID2);
  client.print("/key/");
  client.print(Key2);
  client.print("/temp/");
  client.print(temp2c_min*10);
  client.print("/chill/");
  client.print(chill_c*10);
  client.print("/dew/");
  client.print(dewpt_c*10);
  client.print("/heat/");
  client.print(heat_c*10);
  client.print("/hum/");
  client.print(humidity2);
  client.print("/wspd/");
  client.print(windSpeed*4.47);
  client.print("/wspdavg/");
  client.print(wind_speed_avg*4.47);
  client.print("/wspdhi/");
  client.print(windgustmph*4.47);
  client.print("/wdir/");
  client.print(Winddir);
  client.print("/wdiravg/");
  //client.print(getWindDirectionMax());  
  client.print("/bar/");
  client.print(baromhpa*10); 
//  client.print("/rain/");
//  client.print(rain*10);
//  client.print("/rainrate/");
//  client.print(rainrate*10);
  client.print("/tempin/");
  client.print(temp2c_min*10);
  client.print("/dewin/");
  client.print(dewpt_c*10);
  client.print("/heatin/");
  client.print(heat_c*10);
  client.print("/humin/");
  client.print(humidity2);
  //client.print("/uvi/");
  //client.print(uvi);
  client.println("/ HTTP/1.1");
  client.println("Host: api.weathercloud.net");
  client.println();
  
  Serial.println();
  delay(1000);
 
  if (!client.connected()) {
    Serial.println("client disconected.");
    if (client.connect(server2, 80)) {
      delay(100);
      Serial.print("connected to ");
      Serial.println(client.remoteIP());
    } else {
      Serial.println("connection failed");
    }
  }
//}
//}
  delay(100);
}


//------------------------------------------------------------------------------------------------------------
///////////////////////////////// SEND DATA TO Windy.com ////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------
void windy(void)
{
  //if ( counter == 16)
  //{
    Serial.print("Connecting to ");
    Serial.print(server4);
    Serial.println("...");
    WiFiClient client;
    
    if (client.connect(server4, 80)) {
      Serial.print("Connected to ");
      Serial.println(client.remoteIP());
      delay(100);
    } else {
      Serial.println("connection failed");
    }
  
    client.print("GET /pws/update/");
    client.print(Key4);
    client.print("?winddir=");
    client.print(Winddir);
    client.print("&windspeedmph=");
    client.print(wind_speed_avg);    //avarege
    client.print("&windgustmph=");
    client.print(windgustmph * 4.47);
    client.print("&tempf=");
    client.print(temp_f);
    client.print("&baromin=");
    client.print(baromin);
    client.print("&dewptf=");
    client.print(dewpt_c);
    client.print("&humidity=");
    client.print(humidity2);
    client.print("/ HTTP/1.1\r\nHost: stations.windy.com:80\r\nConnection: close\r\n\r\n");
/*
    Serial.print(server4);
    Serial.print("/pws/update/");
    Serial.print(Key4);
    Serial.print("?winddir=");
    Serial.print(Winddir);
    Serial.print("&windspeedmph=");
    Serial.print(speedkph * 1.609);
    Serial.print("&windgustmph=");
    Serial.print(windgustmph * 4.47);
    Serial.print("&tempf=");
    Serial.print(temp_f);
    Serial.print("&baromin=");
    Serial.print(baromin);
    Serial.print("&dewptf=");
    Serial.print(dewpt_c);
    Serial.print("&humidity=");
    Serial.println(humidity2);
*/
    
    Serial.println();
    delay(1000);
  //}
}


//------------------------------------------------------------------------------------------------------------
///////////////////////////////// SEND DATA TO Pwsweather.com//////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------
void pws(void)
{
  Serial.print("Connecting to ");
  Serial.println(server5);
  WiFiClient client;
  
  if (client.connect(server5, 80)) {
    Serial.print("connected to ");
    Serial.println(client.remoteIP());
    delay(100);
  } else {
    Serial.println("connection failed");
  }
  
  client.print("GET /api/v1/submitwx?");
  client.print("ID=");
  client.print(ID5);
  client.print("&PASSWORD=");
  client.print(Key5);
  client.print("&dateutc=now&winddir=");
  //client.print(CalDirection);
  client.print(Winddir);
  client.print("&tempf=");
  client.print(temp_f);
  client.print("&windspeedmph=");
  client.print(wind_speed_avg);    
  client.print("&windgustmph=");
  client.print(windgustmph);
  client.print("&dewptf=");
  client.print(dewpt_f);
  client.print("&humidity=");
  client.print(humidity2);
  client.print("&baromin=");
  client.print(baromin);
//  client.print("&rainin=");
//  client.print(rain1h);
//  client.print("&dailyrainin=");
//  client.print(rain24h);
  client.print("&softwaretype=NodeMCU-ESP12&action=updateraw");
  client.print("/ HTTP/1.1\r\nHost: pwsupdate.pwsweather.com:80\r\nConnection: close\r\n\r\n");
  
  Serial.println();
  delay(1000);
  
}


//------------------------------------------------------------------------------------------------------------
///////////////////////////////// SEND DATA TO Windguru.cz ///////////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------
void windguru(void)
{
  //if ( counter == 16)
  //{
    Serial.print("Connecting to ");
    Serial.print(server6);
    Serial.println("...");
    WiFiClient client;
    
    if (client.connect(server6, 80)) {
      Serial.print("Connected to ");
      Serial.println(client.remoteIP());
      delay(100);
    } else {
      Serial.println("connection failed");
    }
  
    client.print("GET /upload/api.php");
    client.print("?uid=");
    client.print(ID6);
    client.print("&salt=");
    int salt6 = now();
    client.print(salt6);
    client.print("&hash=");
    String hash6 = md5(String(salt6)+String(ID6)+String(Key6));
    client.print(hash6);
    client.print("&wind_avg=");
    client.print(speedknots);
    //client.print("&wind_min=");
    //client.print(speedknots);
    //client.print("&wind_max=");
    //client.print(speedknots);
    client.print("&wind_direction=");
    client.print(Winddir);
    client.print("&temperature=");
    client.print(temp2c);
    client.print("&rh=");
    client.print(humidity2);
    client.print("&mslp=");
    client.print(baromhpa);
    client.print("/ HTTP/1.1\r\nHost: www.windguru.cz:80\r\nConnection: close\r\n\r\n");
/*    
    Serial.print(server6);
    Serial.print("/upload/api.php");
    Serial.print("?uid=");
    Serial.print(ID6);
    Serial.print("&salt=");
    //int salt6 = now();
    Serial.print(salt6);
    Serial.print("&hash=");
    //String hash6 = md5(String(salt6)+String(ID6)+String(Key6));
    Serial.print(hash6);
    Serial.print("&wind_avg=");
    Serial.print(speedknots);
    //client.print("&wind_min=");
    //client.print(speedknots);
    //client.print("&wind_max=");
    //client.print(speedknots);
    Serial.print("&wind_direction=");
    Serial.print(Winddir);
    Serial.print("&temperature=");
    Serial.print(temp2c);
    Serial.print("&rh=");
    Serial.print(humidity2);
    Serial.print("&mslp=");
    Serial.println(baromhpa);
*/
    Serial.println();
    delay(1000);
  //}
}
