
//------------------------------------------------------------------------------------------------------------
////////////////////////////////////////////////// WIFI SETUP ////////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------
void Start_Wifi()
{
  Serial.print("Connecting to Wifi ");
  delay(1000);

  //inicializa wifi como AP e Station simulatneos
  WiFi.mode(WIFI_AP_STA);
  WiFi.hostname("RioParamotor_Weather_station");
  
  wifiMulti.addAP(ssid1, password1);        //if you have less SSID, delete the others
  wifiMulti.addAP(ssid2, password2);
  wifiMulti.addAP(ssid3, password3);

  while (wifiMulti.run() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.print("  IP address: ");
  Serial.print(WiFi.localIP());
  Serial.print("  MAC address: ");
  Serial.println(WiFi.macAddress());
  
  delay(500);
}


//------------------------------------------------------------------------------------------------------------
////////////////////////////////////////////////// RSSI dBm //////////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------

void get_RSSIdBm() 
{
  while (wifiMulti.run() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  
  dBm = WiFi.RSSI();
  quality = 2 * (dBm + 100);
  if (dBm >= -50)
    quality = 100;
 
}
