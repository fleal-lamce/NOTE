//------------------------------------------------------------------------------------------------------------
////////////////////////////////////////////////// NTP Time //////////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------

//--------------------------------Time  zone ------------------------------------------
const int timeZone = -3;     // GMT-2 Time Zone in Brasilia
int timec;
//const int timeZone = -5;  // Eastern Standard Time (USA)
//const int timeZone = -4;  // Eastern Daylight Time (USA)
//const int timeZone = -8;  // Pacific Standard Time (USA)
//const int timeZone = -7;  // Pacific Daylight Time (USA)

//-----------------------------------NTP Servers---------------------------------------------
static const char ntpServerName[] = "br.pool.ntp.org";

//static const char ntpServerName[] = "pool.ntp.org";
// const char* ntpServerName = "time.nist.gov";
//const char* ntpServerName = "time.google.com";
//const char* ntpServerName = "us.pool.ntp.org";
//static const char ntpServerName[] = "time.nist.gov";
//static const char ntpServerName[] = "time-a.timefreq.bldrdoc.gov";
//static const char ntpServerName[] = "time-b.timefreq.bldrdoc.gov";
//static const char ntpServerName[] = "time-c.timefreq.bldrdoc.gov";


//------------------------------------------------------------------------------------------------------------
//////////////////////////////////////////////  Time NTP ////////////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------
void Start_Ntp()
{
  Udp.begin(localPort);
  setSyncProvider(getNtpTime);
  setSyncInterval(300);

  //horario de verão
//  if (month() < 4 || month() >= 11) 
//  {
//    timec = timeZone; // Winter time
//  }
//  else 
//  {
//    timec = timeZone + 1 ;  //Summer time
//  }

  Udp.begin(localPort);
  
  Serial.print(" local port ");
  Serial.println(Udp.localPort());
  Serial.println("waiting for sync");
  setSyncProvider(getNtpTimez);
  setSyncInterval(300);

  DigitalClockDisplay();
  
}


//-----------------------------------------------------------
void time_ntp(void)
{
  if (timeStatus() != timeNotSet) {
    if (now() != prevDisplay) { //update the display only if time has changed
      prevDisplay = now();
      digitalClockDisplay();
    }
  }  
}


//-----------------------------------------------------------
void DigitalClockDisplay()
{
  // digital clock display of the time
  Serial.print("  NTP Time: ");
  Serial.print(hour());
  printDigits(minute());
  printDigits(second());
  Serial.print("  ");
  Serial.print(day());
  Serial.print("/");
  Serial.print(month());
  Serial.print("/");
  Serial.print(year());
  Serial.println();
}


//-----------------------------------------------------------
void printDigits(int digits)
{
  // utility for digital clock display: prints preceding colon and leading 0
  Serial.print(":");
  if (digits < 10)
    Serial.print('0');
  Serial.print(digits);
}


//------------------------------------------------------------------------------------------------------------
//////////////////////////////////////////////  NTP Code  ////////////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------

const int NTP_PACKET_SIZE = 48; // NTP time is in the first 48 bytes of message
byte packetBuffer[NTP_PACKET_SIZE]; //buffer to hold incoming & outgoing packets

//-----------------------------------------------------------
time_t getNtpTime()
{
  IPAddress ntpServerIP; // NTP server's ip address

  while (Udp.parsePacket() > 0) ; // discard any previously received packets
  
  // get a random server from the pool
  WiFi.hostByName(ntpServerName, ntpServerIP);
  
  Serial.print("Transmit NTP Request to  ");
  Serial.print(ntpServerName);
  Serial.print(" - ");
  Serial.println(ntpServerIP);
  
  sendNTPpacket(ntpServerIP);
  
  uint32_t beginWait = millis();
  while (millis() - beginWait < 1500) {
    int size = Udp.parsePacket();
    if (size >= NTP_PACKET_SIZE) {
      Serial.print("  Receive NTP Response: ");
      Udp.read(packetBuffer, NTP_PACKET_SIZE);  // read packet into the buffer
      unsigned long secsSince1900;
      // convert four bytes starting at location 40 to a long integer
      secsSince1900 =  (unsigned long)packetBuffer[40] << 24;
      secsSince1900 |= (unsigned long)packetBuffer[41] << 16;
      secsSince1900 |= (unsigned long)packetBuffer[42] << 8;
      secsSince1900 |= (unsigned long)packetBuffer[43];
      return secsSince1900 - 2208988800UL + timeZone * SECS_PER_HOUR;
    }
  }
  Serial.println("No NTP Response :-(");
  return 0; // return 0 if unable to get the time
}


//-----------------------------------------------------------
time_t getNtpTimez()
{
  IPAddress ntpServerIP; // NTP server's ip address

  while (Udp.parsePacket() > 0) ; // discard any previously received packets
  
  // get a random server from the pool
  WiFi.hostByName(ntpServerName, ntpServerIP);
  
  Serial.print("Transmit NTP Request to  ");
  Serial.print(ntpServerName);
  Serial.print(" - ");
  Serial.println(ntpServerIP);
  
  sendNTPpacket(ntpServerIP);
  
  uint32_t beginWait = millis();
  while (millis() - beginWait < 1500) {
    int size = Udp.parsePacket();
    if (size >= NTP_PACKET_SIZE) {
      Serial.print("  Receive NTP Response: ");
      Udp.read(packetBuffer, NTP_PACKET_SIZE);  // read packet into the buffer
      unsigned long secsSince1900;
      // convert four bytes starting at location 40 to a long integer
      secsSince1900 =  (unsigned long)packetBuffer[40] << 24;
      secsSince1900 |= (unsigned long)packetBuffer[41] << 16;
      secsSince1900 |= (unsigned long)packetBuffer[42] << 8;
      secsSince1900 |= (unsigned long)packetBuffer[43];
      return secsSince1900 - 2208988800UL + timec * SECS_PER_HOUR;
    }
  }
  Serial.println("No NTP Response :-(");
  return 0; // return 0 if unable to get the time
}


//-----------------------------------------------------------
// send an NTP request to the time server at the given address
void sendNTPpacket(IPAddress &address)
{
  // set all bytes in the buffer to 0
  memset(packetBuffer, 0, NTP_PACKET_SIZE);
  
  // Initialize values needed to form NTP request
  // (see URL above for details on the packets)
  packetBuffer[0] = 0b11100011;   // LI, Version, Mode
  packetBuffer[1] = 0;     // Stratum, or type of clock
  packetBuffer[2] = 6;     // Polling Interval
  packetBuffer[3] = 0xEC;  // Peer Clock Precision
  // 8 bytes of zero for Root Delay & Root Dispersion
  packetBuffer[12] = 49;
  packetBuffer[13] = 0x4E;
  packetBuffer[14] = 49;
  packetBuffer[15] = 52;
  
  // all NTP fields have been given values, now
  // you can send a packet requesting a timestamp:
  Udp.beginPacket(address, 123); //NTP requests are to port 123
  Udp.write(packetBuffer, NTP_PACKET_SIZE);
  Udp.endPacket();
}
