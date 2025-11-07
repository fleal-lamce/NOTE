unsigned int scounter = 0;       //Contador para o sensor  

//-------------------------------------------------------------------------------------------------------------
////////////////////////////////////Get wind speed  /////////////////////////////////////////////////////////
//-------------------------------------------------------------------------------------------------------------
void getWindSpeed(void)
{
 
  Rotations = 0; // Set Rotations count to 0 ready for calculations
  //sei(); // Enables interrupts
  ArduinoOTA.handle();
  delay (5000); // Wait 5 seconds to average wind speed
  ArduinoOTA.handle();
  delay (5000); // Wait 5 seconds to average wind speed
  ArduinoOTA.handle();
  delay (5000); // Wait 5 seconds to average wind speed
  ArduinoOTA.handle();
  delay (5000); // Wait 5 seconds to average wind speed
  ArduinoOTA.handle();
  delay (5000); // Wait 5 seconds to average wind speed
  ArduinoOTA.handle();
  delay (5000); // Wait 5 seconds to average wind speed
  //cli(); // Disable interrupts

  Serial.print("Rotations: ");
  Serial.print(Rotations);
     
  /* convert to mp/h using the formula V=P(2.25/T)
  V = P(2.25/30) = P * 0.075       V - speed in mph,  P - pulses per sample period, T - sample period in seconds */
  windSpeed = Rotations * 0.15; // 30 seconds
  Rotations = 0;   // Reset count for next sample
     
  Serial.print("  windSpeed: ");
  Serial.println(windSpeed);
  
  if (windSpeed > windgustmph) {
     windgustmph = windSpeed;
  }
  if (wind_speed_min > windSpeed ) {
     wind_speed_min = windSpeed;
  }

  wind_speed_avg = (windgustmph + wind_speed_min) * 0.5;   // average wind speed mph per 10 minutes

}


// This is the function that the interrupt calls to increment the rotation count
//-------------------------------------------------------------------------------------------------------------
////////////////////////////////////ISR rotation//////////////////////////////////////////////////////////////
//-------------------------------------------------------------------------------------------------------------
void ICACHE_RAM_ATTR isr_rotation(void)   
{
  if ((millis() - ContactBounceTime) > 30 ) {  // debounce the switch contact.
    Rotations++;
    ContactBounceTime = millis();
  }
}


//---------------------------------------------------
// Convert MPH to Knots
float getKnots(float speed) 
{
   return speed * 0.868976;          //knots 0.868976;
}


//---------------------------------------------------
// Convert MPH to m/s
float getms(float speed) 
{
   return speed * 0.44704;           //metric m/s 0.44704;;
}


//---------------------------------------------------
// converts wind speed to wind strength
void getWindStrength(float speed)
{
  if(speed < 1)                         Serial.println("Calm");
  else if(speed >=  1 && speed <  3)    Serial.println("Light Air");
  else if(speed >=  3 && speed <  7)    Serial.println("Light Breeze");
  else if(speed >=  7 && speed < 12)    Serial.println("Gentle Breeze");
  else if(speed >= 12 && speed < 18)    Serial.println("Moderate Breeze");
  else if(speed >= 18 && speed < 24)    Serial.println("Fresh Breeze");
  else if(speed >= 24 && speed < 31)    Serial.println("Strong Breeze");
  else if(speed >= 31 && speed < 38)    Serial.println("High wind");
  else if(speed >= 38 && speed < 46)    Serial.println("Fresh Gale");
  else if(speed >= 46 && speed < 54)    Serial.println("Strong Gale");
  else if(speed >= 54 && speed < 63)    Serial.println("Storm");
  else if(speed >= 63 && speed < 72)    Serial.println("Violent storm"); 
  else if(speed >= 72 && speed)         Serial.println("Hurricane");    
}



//-------------------------------------------------------------------------------------------------------------
////////////////////////////////////Get wind speed  /////////////////////////////////////////////////////////
//-------------------------------------------------------------------------------------------------------------
// by ggcvirtual

//---------------------------------------------------
//Função para medir velocidade do vento
void getWindSpeedNEW()
{
  speedmps = 0;
  speedkph = 0;
  speedknots = 0;
  
  scounter = 0;  
  //attachInterrupt(0, addcount, RISING);
  //attachInterrupt(digitalPinToInterrupt(pinS), funcaoInterrupcao, RISING);
  attachInterrupt(digitalPinToInterrupt(WindSensorPin), funcaoInterrupcao, RISING);
  //attachInterrupt(digitalPinToInterrupt(WindSensorPin), isr_rotation, RISING);
  
  //Serial.println("millis 1");
 
  unsigned long millis();       
  unsigned long startTime = millis();
  unsigned long endTime = millis();
  //Serial.println("millis 2");
  while(endTime < startTime + period) {
    endTime = millis();
    //Serial.print(endTime);
    //Serial.print(" < ");
    //Serial.print(startTime);
    //Serial.print(" + ");
    //Serial.print(period);
    //Serial.print(" = ");
    //Serial.println(startTime + period);
    delay(30);
    }
  //Serial.println("millis 3");

  //Função para calcular o RPM
  RPM=((scounter)*60)/(period/1000);  // Calculate revolutions per minute (RPM)

  //Velocidade do vento em m/s
  speedmps = ((4 * pi * radius * RPM)/60) / 1000;  //Calcula a velocidade do vento em m/s
 
  //Velocidade do vento em km/h
  speedkph = (((4 * pi * radius * RPM)/60) / 1000)*3.6;  //Calcula velocidade do vento em km/h
  
  //Velocidade do vento em milhas/h
  speedmph = speedkph / 1.609 ;  //Calcula velocidade do vento em milhas/h
 
  //Velocidade do vento em knots
  speedknots = speedkph / 1.852;  //Calcula velocidade do vento em knots

  Serial.print(" WindSpeed: ");
  Serial.print(RPM);
  Serial.print(" rpm  ");
  Serial.print(speedmps);
  Serial.print(" m/s  ");
  Serial.print(speedkph);
  Serial.print(" km/h  ");
  Serial.print(speedknots);
  Serial.println(" knots");

  //calcula velocidade das rajadas e velocidade media
  if (speedmph > windgustmph) {
     windgustmph = speedmph;
  }
  if (wind_speed_min > speedmph ) {
     wind_speed_min = speedmph;
  }

  wind_speed_avg = (windgustmph + wind_speed_min) * 0.5;   // velocidade media em mph em 5 minutos


} //end WinsSpeed

 
//---------------------------------------------------
//Declaração da Função de Interrupção
//void ICACHE_RAM_ATTR funcaoInterrupcao(); //função de Interrupção armazenada na RAM
void ICACHE_RAM_ATTR funcaoInterrupcao()
{
  scounter++;                          
  //Serial.print("scounter: ");
  //Serial.println(scounter);
}


//-------------------------------------------------------------------------------------------------------------
/////////////////////////////////// Wind direction ////////////////////////////////////////////////////////////
//-------------------------------------------------------------------------------------------------------------
void getWindDirectionNEW(void) 
{
  vane_value = analogRead(A0);
  Serial.print(" WindDirection: ");
  Serial.print(vane_value);
  
  if(vane_value < rmin){rmin = vane_value;}
  if(vane_value > rmax){rmax = vane_value;}
  Serial.print("  [");  
  Serial.print(rmin);
  Serial.print(" ");  
  Serial.print(rmax);
  Serial.print("]  ");  

  // valores obtidos no NodeMCU + 4k7
  if (vane_value <= 231)      { Winddir =  45; WindN = "NE"; }
  else if (vane_value <= 257) { Winddir =  90; WindN = "E "; }
  else if (vane_value <= 290) { Winddir = 135; WindN = "SE"; }
  else if (vane_value <= 335) { Winddir = 180; WindN = "S "; }
  else if (vane_value <= 397) { Winddir = 225; WindN = "SO"; }
  else if (vane_value <= 488) { Winddir = 270; WindN = "O "; }
  else if (vane_value <= 633) { Winddir = 315; WindN = "NO"; }
  else                        { Winddir =   0; WindN = "N "; }

  Serial.print(Winddir);
  Serial.print("°  ");  
  Serial.println(WindN);

}
