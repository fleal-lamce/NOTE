/*
//------------------------------------------------------------------------------------------------------------
///////////////////////////////// Get Rain data //////////////////////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------
void getRain(void)
{
  cli();         //Disable interrupts
      
  rainrate = tipCount1h * Bucket_Size_EU;   
  rain1h = tipCount1h * Bucket_Size_US;    // 0.3/25.4 = 0.012 bucket size inches
  rain = tipCount24h * Bucket_Size_EU;
  rain24h = tipCount24h * Bucket_Size_US;  // 0.3/25.4 = 0.012 bucket size inches
  
  if (minute() >= 59)
  {
    Serial.println("Reset Hourly Rain");
    tipCount1h = 0; //reset  Rain counter each 1h
    eepromstring = String(tipCount1h,2);
    eepromSet("tipCount1h", eepromstring);
  
    for (int i = 0; i < sizeof(windDirections) / sizeof(windDirections[0]); i++)
    {
      windDirections[i] = 0;  //reset  Wind direction average  each 1h
    } 
  }

  if ((hour() >= 23) && (minute() >= 59))    //reset Daily Rain each 24
  {
    Serial.println("Reset Daily Rain");
    tipCount1h = 0;
    tipCount24h = 0;

    eepromstring = String(tipCount24h,2);
    eepromSet("tipCount24h", eepromstring);
    eepromstring = String(tipCount1h,2);
    eepromSet("tipCount1h", eepromstring);
    Serial.println("CLEAR eeprom ");
    eepromClear();

    delay(100);
    ESP.restart();
  }
  sei();         //Enables interrupts
}


//------------------------------------------------------------------------------------------------------------
/////////////////////////////////////// RAIN Interrupt ///////////////////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------

// Interrrupt handler routine that is triggered when the W174 detects rain   

void ICACHE_RAM_ATTR isr_rg() 
{
  if((millis() - contactTime) > 2000 ) { // debounce of sensor signal 
    tipCount1h++;
    tipCount24h++;
    
    //STORE RAINCOUNT IN EEPROM
    //Serial.println("SET EEPROM");
    eepromstring = String(tipCount24h,2);
    eepromSet("tipCount24h", eepromstring);
    eepromstring = String(tipCount1h,2);
    eepromSet("tipCount1h", eepromstring);
    //END - STORE RAINCOUNT IN EEPROM
   
    contactTime = millis(); 
  } 
} 

*/
