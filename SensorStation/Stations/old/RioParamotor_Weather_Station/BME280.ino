//-------------------------------------------------------------------------------------------------------------
//////////////////////////////////// GY-BME280 Sensor /////////////////////////////////////////////////////////
//-------------------------------------------------------------------------------------------------------------

void Start_BME280()
{
   //Wire.begin(D2,D1); 
  
  //if (!bme.begin()) {
  if (! bme.begin(0x76, &Wire)) {
    Serial.println("*****************************************************");
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    Serial.println("*****************************************************");
    //while (1);
  }
  
//  bme.setTempCal(-1);
//  bme.begin();
}


//-------------------------------------------------------------------------------------------------------------
//////////////////////////////////// Read the Data from Sensors ///////////////////////////////////////////////
//-------------------------------------------------------------------------------------------------------------
void read_BME280(void)
{
  
  //bme.readSensor();
  //delay(500); 
  
  //baromhpa = bme.getPressure_MB()+(altitudepws * 0.12);   // preassure from BME280 sensor
  baromhpa = bme.readPressure() / 100.0F;   // preassure from BME280 sensor
  if (baromhpa < 950 || baromhpa > 1050 ) {
    baromhpa = last_baromhpa;
  }
  last_baromhpa = baromhpa;
  baromin = (baromhpa)/ 33.86;
  
  //temp2c = bme.getTemperature_C();    // temperature from BME280 sensor
  temp2c = bme.readTemperature();    // temperature from BME280 sensor
  
  temp2c = (temp2c - 1);
  if (temp2c_min > temp2c ) {
    temp2c_min = temp2c;
  }

  temp_f =  (temp2c_min * 9.0)/ 5.0 + 32.0;   //  converting dew point to F

  //humidity2 = bme.getHumidity();      // humidity from BME280 sensor
  humidity2 = bme.readHumidity();      // humidity from BME280 sensor
     
  Serial.print(F(" Temperature: ")); Serial.print(temp2c); Serial.print(" °C, "); Serial.print(temp_f); Serial.println(" °F  "); 
  Serial.print(F(" Humidity: "));    Serial.print(humidity2); Serial.println(" %  ");
  Serial.print(F(" Pressure: "));    Serial.print(baromhpa);Serial.print(" hPa, "); Serial.print(baromin); Serial.println(" inHg  ");
  
  dewpt_c = (dewPoint(temp2c_min, humidity2));  //dew point
  dewpt_f = (dewpt_c * 9.0)/ 5.0 + 32.0;      //  converting dew point to F
  Serial.print(" Dew point: "); Serial.print(dewpt_c); Serial.print(" °C "); Serial.print(dewpt_f); Serial.println(" °F ");
  
  windchill();
  Serial.print(" Wind chill: "); Serial.print(chill_c); Serial.println(" °C ");
  
  heatindex();
  Serial.print(" Heat index: "); Serial.print(heat_c); Serial.println(" °C "); 
  
  //Counter();

}

//-------------------------------- Heat Index ---------------------------------------------
#define c1 (-42.379)
#define c2 (2.04901523)
#define c3 (10.14333127)
#define c4 (-0.22475541)
#define c5 (-0.00683783)
#define c6 (-0.05481717)
#define c7 (0.00122874)
#define c8 (0.00085282)
#define c9 (-0.00000199)

//------------------------------------------------------------------------------------------------------------
/////////////////////////////////////////////// Calculate Heat Index  ///////////////////////////////////////
//------------------------------------------------------------------------------------------------------------
void heatindex()
{
  if (temp_f > 80.0)   //The heat index only works for temperatures  above 80°F 
  {
    heat_f = c1+c2*(temp_f)+c3*(humidity2)+c4*(temp_f)*(humidity2)+c5*(pow(temp_f,2))+c6*(pow(humidity2,2))+c7*(pow(temp_f, 2))*(humidity2)+c8*(temp_f)*(pow(humidity2, 2))+c9*(pow(temp_f, 2))*(pow(humidity2, 2));
    heat_c = (heat_f - 32)*5/9;  //  converting to C
    }
    else
  {
    heat_c = temp2c_min;
  }
}


// calcula sensação térmica
//------------------------------------------------------------------------------------------------------------
/////////////////////////////////////////////// Calculate Windchill  ////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------
void windchill()
{
  if ((temp_f <50.0) && (windgustmph > 3.0)) //The wind chill only works for temperatures  below 50°F and wind speed above 3 mph. (10°C , 1 m/s)
  {
    chill_f =35.74+0.6215*temp_f-35.75*pow(wind_speed_avg,0.16)+0.4275*temp_f*pow(wind_speed_avg,0.16);
    chill_c = (chill_f - 32)*5/9;  //  converting to C
  } 
  else
  {
    chill_c = temp2c_min;
  }
}


//------------------------------------------------------------------------------------------------------------
/////////////////////////////////////////////// Calculate dew Point C ////////////////////////////////////////
//------------------------------------------------------------------------------------------------------------
double dewPoint(double tempc_min, double humidity)
{
  double RATIO = 373.15 / (273.15 + tempc_min);  // RATIO was originally named A0, possibly confusing in Arduino context
  double SUM = -7.90298 * (RATIO - 1);
  SUM += 5.02808 * log10(RATIO);
  SUM += -1.3816e-7 * (pow(10, (11.344 * (1 - 1/RATIO ))) - 1) ;
  SUM += 8.1328e-3 * (pow(10, (-3.49149 * (RATIO - 1))) - 1) ;
  SUM += log10(1013.246);
  double VP = pow(10, SUM - 3) * humidity;
  double T = log(VP/0.61078);   // temp var
  return (241.88 * T) / (17.558 - T);
}




/*
 * funcionou separadamente
 * biblioteca mais simples
 * 
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME280 bme; // I2C
//Adafruit_BME280 bme(BME_CS); // hardware SPI
//Adafruit_BME280 bme(BME_CS, BME_MOSI, BME_MISO, BME_SCK); // software SPI


void init_bme280()
{
  if (! bme.begin(0x76, &Wire)) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1);
  }
}

void printValues() {
    //Serial.print("Temperature = ");
    Serial.print(bme.readTemperature());
    Serial.print(" °C | ");

    //Serial.print("Humidity = ");
    Serial.print(bme.readHumidity());
    Serial.print(" % |");
    
    //Serial.print("Pressure = ");
    Serial.print(bme.readPressure() / 100.0F);
    Serial.print(" hPa | ");

    //Serial.print("Approx. Altitude = ");
    //Serial.print(bme.readAltitude(SEALEVELPRESSURE_HPA));
    //Serial.print(" m   ");

    Serial.println();
}

*/
