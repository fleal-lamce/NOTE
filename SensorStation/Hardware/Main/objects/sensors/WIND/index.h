#ifndef WIND_H
#define WIND_H
#include <Arduino.h>
#include <string.h>
#include "../../../utils/listener/index.h"

// amarelo -> 5V
// preto   -> GND
// Desencapado -> GND
// verde -> analogico
// vermelho -> pino digital com input pullup (pulsos) (velocity)

class WindStation{
  private:
    class Velocity{
      public:
        const int pin;
        float value;
        char status[16];

        Velocity(int _pin):
            pin(_pin){}

        void setup(){
            pinMode(pin,  INPUT_PULLUP);
        }

        void update(){
            static Listener listener = Listener(15000);
            static bool state  = false;
            static int counter = 0;
            const bool signal  = !digitalRead(pin);

            if(signal != state){
                state = signal;

                if(signal)
                    counter++;
            }

            if(listener.ready(false)){
                const float t = listener.getSec();
                listener.reset();

                value   = counter/t * 1000;
                counter = 0;
                setStatus();
                Serial.println(status);
            }
        }
            
        void setStatus(){
            if(value < 1.0f)
                strcpy(status, "calm");
            else if (value < 3.0f)   
                strcpy(status, "Light Air");
            else if (value < 7.0f)
                strcpy(status, "Light Breeze");
            else if (value < 12.0f)
                strcpy(status, "Gentle Breeze");
            else if (value < 18.0f)
                strcpy(status, "Moderate Breeze");
            else if (value < 24.0f)
                strcpy(status, "Fresh Breeze");
            else if (value < 31.0f)
                strcpy(status, "Strong Breeze");
            else if (value < 38.0f)
                strcpy(status, "High Wind");
            else if (value < 46.0f)
                strcpy(status, "Fresh Gale");
            else if (value < 54.0f)
                strcpy(status, "Strong Gale");
            else if (value < 63.0f)
                strcpy(status, "Storm");
            else if (value < 72.0f)
                strcpy(status, "Violent Storm");
            else
                strcpy(status, "Hurricane");
        }
    };

    class Direction{
      public:
        const int pin;
        float value;
        int digital;
        char status[4];

        Direction(int _pin):
            pin(_pin){}

        void setup(){
            pinMode(pin,  INPUT);
        }

        void update(){
            value = analogRead(pin);
            setStatus();
        }

        void setStatus(){
            static Listener listener = Listener(2000);

            if(!listener.ready())
                return;

            if(value <= 231)
                {digital =  45; strcpy(status, "NE");}
            else if(value <= 257)
                {digital =  90; strcpy(status, "E ");}
            else if(value <= 290)
                {digital = 135; strcpy(status, "SE");}
            else if(value <= 335) 
                {digital = 180; strcpy(status, "S ");}
            else if(value <= 397)
                {digital = 225; strcpy(status, "SO");}
            else if (value <= 488)
                {digital = 270; strcpy(status, "O ");}
            else if(value <= 633) 
                {digital = 315; strcpy(status, "NO");}
            else
                {digital = 0; strcpy(status, "N ");}
        }
    };

  public:
    Velocity velocity;
    Direction direction;

    WindStation(int vel_pin, int dir_pin):
        velocity(vel_pin),
        direction(dir_pin){}

    void setup(){
        velocity.setup();
        direction.setup();
    }

    void handle(){
        velocity.update();
        direction.update();
    }
};


#endif