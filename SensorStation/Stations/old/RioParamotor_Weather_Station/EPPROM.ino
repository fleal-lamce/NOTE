
void  StartEPROM()
{
  EEPROM.begin(512);
  
  //RESET EEPROM CONTENT - ONLY EXECUTE ONE TIME - AFTER COMMENT
  //Serial.println("CLEAR ");
  //eepromClear();
  //END - RESET EEPROM CONTENT - ONLY EXECUTE ONE TIME - AFTER COMMENT
  
  //GET STORED RAINCOUNT IN EEPROM
  //Serial.println("EEPROM Rain value");
  //eepromstring=eepromGet("tipCount1h");
  //tipCount1h=eepromstring.toFloat();
  //Serial.print("tipCount1h VALUE FROM EEPROM: ");
  //Serial.print(tipCount1h);
  //Serial.println("mm");
  
  //eepromstring=eepromGet("tipCount24h");
  //tipCount24h=eepromstring.toFloat();
  //Serial.print("tipCount24h VALUE FROM EEPROM: ");
  //Serial.print(tipCount24h);
  //Serial.println("mm");

}



//------------------------------------------------------------------------------------------------------------
////////////////////////////////////////////////// EEPROM //////////////////////////////////////////////////
void eepromSet(String name, String value)
{
  //Serial.println("eepromSet");
  
  String list=eepromDelete(name);
  String nameValue="&" + name + "=" + value;
  //Serial.println(list);
  //Serial.println(nameValue);
  list+=nameValue;
  for (int i = 0; i < list.length(); ++i){
    EEPROM.write(i,list.charAt(i));
  }
  EEPROM.commit();
  //Serial.print(name);
  //Serial.print(":");
  //Serial.println(value);
}


String eepromDelete(String name)
{
  //Serial.println("eepromDelete");
  
  int nameOfValue;
  String currentName="";
  String currentValue="";
  int foundIt=0;
  char letter;
  String newList="";
  for (int i = 0; i < 512; ++i){
    letter= char(EEPROM.read(i));
    if (letter=='\n'){
      if (foundIt==1){
      }else if (newList.length()>0){
        newList+="=" + currentValue;
        }
        break;
      } else if (letter=='&'){
        nameOfValue=0;
        currentName="";
        if (foundIt==1){
          foundIt=0;
        }else if (newList.length()>0){
           newList+="=" + currentValue;
        }
      } else if (letter=='='){
        if (currentName==name){
           foundIt=1;
        }else{
           foundIt=0;
           newList+="&" + currentName;
        }
        nameOfValue=1;
        currentValue="";
      }
      else{
        if (nameOfValue==0){
          currentName+=letter;
        }else{
          currentValue+=letter;
        }
      } 
  }
  for (int i = 0; i < 512; ++i){
    EEPROM.write(i,'\n');
  }
  EEPROM.commit();
  for (int i = 0; i < newList.length(); ++i){
    EEPROM.write(i,newList.charAt(i));
  }
  EEPROM.commit();
  //Serial.println(name);
  //Serial.println(newList);
  return newList;
}


void eepromClear()
{
  //Serial.println("eepromClear");
  for (int i = 0; i < 512; ++i){
    EEPROM.write(i,'\n');
  }
}


String eepromList()
{
  //Serial.println("eepromList");
  char letter;
  String list="";
  for (int i = 0; i < 512; ++i){
      letter= char(EEPROM.read(i));
      if (letter=='\n'){
        break;
      }else{
        list+=letter;
      } 
  }
  //Serial.println(list);
  return list;
}


String eepromGet(String name)
{
  //Serial.println("eepromGet");
  
  int nameOfValue;
  String currentName="";
  String currentValue="";
  int foundIt=0;
  String value="";
  char letter;
  for (int i = 0; i < 512; ++i){
      letter= char(EEPROM.read(i));
      if (letter=='\n'){
        if (foundIt==1){
          value=currentValue; 
        }
        break;
      } else if (letter=='&'){
        nameOfValue=0;
        currentName="";
        if (foundIt==1){
          value=currentValue;
          break; 
        }
      } else if (letter=='='){
        if (currentName==name){
           foundIt=1;
        }else{
        }
        nameOfValue=1;
        currentValue="";
      }
      else{
        if (nameOfValue==0){
          currentName+=letter;
        }else{
          currentValue+=letter;
        }
      } 
  }
  //Serial.print(name);
  //Serial.print(":");
  //Serial.println(value);
  return value;
}
