#include <Adafruit_Fingerprint.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>


char selecao;

SoftwareSerial mySerial(2, 3);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

LiquidCrystal_I2C lcd(0x27,20,4);

void setup() {
  lcd.init();
  lcd.backlight();
  finger.begin(57600);
  Serial.begin(9600);
  if (finger.verifyPassword()) {
    Serial.println("Found fingerprint sensor!");
  } else {
    Serial.println("Did not find fingerprint sensor :(");
    while (1) { delay(1); }
  }
  finger.getTemplateCount();

  if (finger.templateCount == 0) {
    Serial.println("Sensor doesn't contain any fingerprint data. Please run the 'enroll' example.");
  }
  else {
    Serial.println("Waiting for valid finger...");
      Serial.print("Sensor contains "); Serial.print(finger.templateCount); Serial.println(" templates");
  }

}

void loop() {

  if (Serial.available() > 0) {
    selecao = Serial.read();
  }

 
  if (selecao != 'l' && selecao != 'k') {
      getFingerID(); 
      delay(50); 
  }

  if (selecao == 'l') {
    lcd.clear();
    lcd.setCursor(2, 0);
    lcd.print("Cadastrar Biometria:");
    getFinger(); 
    lcd.clear();
    selecao = 0; 
  }

  if (selecao == 'k') {
    lcd.clear();
    lcd.setCursor(2, 0);
    lcd.print("Deletando:");
    
    delay(1000); 

    while (Serial.available() == 0); 

    uint8_t idParaDeletar = Serial.read(); 

    if (idParaDeletar > 0 && idParaDeletar <= 255) {
        Serial.print("Recebido pedido para deletar ID: ");
        Serial.println(idParaDeletar);
        
        deleteFinger(idParaDeletar); 
    } else {
        Serial.print("ID Invalido recebido: ");
        Serial.println(idParaDeletar);
        lcd.clear();
        lcd.print("ID Invalido");
        delay(2000);
    }
    selecao = 0; 
  }
}
uint8_t getID(){
  int id;
 for (int idTest = 1; idTest < 50; idTest++) {

  uint8_t p = finger.loadModel(idTest);
  switch (p) {
    case FINGERPRINT_OK:
      break;
    case FINGERPRINT_PACKETRECIEVEERR:
      return p;
    default:
      return idTest;
  }
 }
  Serial.println("sem IDs livres");
  return 0;
}

uint8_t getFinger(){
  int id = getID();

  if(id == 0){
    Serial.println("Id invalido: ");
    return true;
  }

  int p = -1;
  char idProf = 0;
  char terCads = 0;
  char idLoop = 0;

  if (Serial.available() > 0) {
    idProf = Serial.read();
  }


  while (true) {
    if (Serial.available() > 0) {
      terCads = Serial.read();
      if (terCads == 'i') {
        break;
      }
    }
    delay(10);
  }
  if (terCads != 'i') {
    Serial.println("Timeout esperando confirmação");
    return true;
  }

  lcd.clear();
  lcd.setCursor(1,0);
  lcd.print("Coloque o Dedo:");


  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
    case FINGERPRINT_OK:
      break;
    case FINGERPRINT_NOFINGER:
      break;
    case FINGERPRINT_PACKETRECIEVEERR:
      lcd.setCursor(2, 0);
      lcd.print("Houve algum");
      lcd.setCursor(3, 1);
      lcd.print("Erro!!");
      delay(3000);
      break;
    case FINGERPRINT_IMAGEFAIL:
      lcd.setCursor(2, 0);
      lcd.print("Houve algum");
      lcd.setCursor(3, 1);
      lcd.print("Erro!!");
      delay(3000);
      break;
    default:
      lcd.setCursor(2, 0);
      lcd.print("Houve algum");
      lcd.setCursor(3, 1);
      lcd.print("Erro!!");
      delay(3000);
      break;
    }
  }

  p = finger.image2Tz(1);
  switch (p) {
    case FINGERPRINT_OK:
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
       lcd.clear();
      lcd.setCursor(1,0);
      lcd.print("Houve um erro nos pacotes:");
      delay(2000);
      return p;
    case FINGERPRINT_FEATUREFAIL:
      lcd.clear();
      lcd.setCursor(1,0);
      lcd.print("Houve um erro:");
      delay(2000);
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      lcd.clear();
      lcd.setCursor(1,0);
      lcd.print("Houve um erro:");
      delay(2000);
      return p;
    default:
      return p;
  }

  lcd.clear();
  lcd.setCursor(1,0);
  lcd.print("Remova o Dedo:");
  delay(2000);
  p = 0;
  while (p != FINGERPRINT_NOFINGER) {
    p = finger.getImage();
  }
  p = -1;
  lcd.clear();
  lcd.setCursor(1,0);
  lcd.print("Coloque DNV o Dedo:");
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
    case FINGERPRINT_OK:
      break;
    case FINGERPRINT_NOFINGER:
      break;
    case FINGERPRINT_PACKETRECIEVEERR:
      lcd.setCursor(2, 0);
      lcd.print("Houve algum");
      lcd.setCursor(3, 1);
      lcd.print("Erro!!");
      delay(3000);
      break;
    case FINGERPRINT_IMAGEFAIL:
      lcd.setCursor(2, 0);
      lcd.print("Houve algum");
      lcd.setCursor(3, 1);
      lcd.print("Erro!!");
      delay(3000);
      break;
    default:
      lcd.setCursor(2, 0);
      lcd.print("Houve algum");
      lcd.setCursor(3, 1);
      lcd.print("Erro!!");
      delay(3000);
      break;
    }
  }

  p = finger.image2Tz(2);
  switch (p) {
    case FINGERPRINT_OK:
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_FEATUREFAIL:
      Serial.println("Could not find fingerprint features");
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.println("Could not find fingerprint features");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }


  p = finger.createModel();
  if (p != FINGERPRINT_OK) {
    switch (p) {
      case FINGERPRINT_PACKETRECIEVEERR:
        lcd.setCursor(2, 0);
        lcd.print("Houve algum");
        lcd.setCursor(3, 1);
        lcd.print("Erro!!");
        delay(3000);
        break;
      case FINGERPRINT_ENROLLMISMATCH:
        lcd.setCursor(2, 0);
        lcd.print("Houve algum");
        lcd.setCursor(3, 1);
        lcd.print("Erro!!");
        delay(3000);
        break;
      default:
        lcd.setCursor(2, 0);
        lcd.print("Houve algum");
        lcd.setCursor(3, 1);
        lcd.print("Erro!!");
        delay(3000);
        break;
    }
    return p;
  }

  p = finger.storeModel(id);
  if (p == FINGERPRINT_OK) {
     lcd.clear();
     lcd.setCursor(1,0);
     lcd.print("Dedo Salvo");
     delay(1000);

  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_BADLOCATION) {
    Serial.println("Could not store in that location");
    return p;
  } else if (p == FINGERPRINT_FLASHERR) {
    Serial.println("Error writing to flash");
    return p;
  } else {
    Serial.println("Unknown error");
    return p;
  }

 while (true) {
    if (Serial.available() > 0) {
      idLoop = Serial.read();
      if (idLoop == 'u') {
        break;
      }
    }
    delay(700);
    Serial.println(id);
    delay(2100);
  }
  return true;

}

uint8_t getFingerID() {
  uint8_t p = finger.getImage();
  
  if (p != FINGERPRINT_OK) return p;

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK) return p;

  p = finger.fingerSearch();

  if (p == FINGERPRINT_OK) {
    Serial.println(finger.fingerID);
    
    while(Serial.available() > 0) { Serial.read(); }

    char ver_horario = 0;
    unsigned long tempo_inicio = millis();
    bool respondeu = false;

    while (millis() - tempo_inicio < 3000) { 
      if (Serial.available() > 0) {
        ver_horario = Serial.read();
        
        if (ver_horario == 'n') {
          lcd.clear();
          lcd.setCursor(2, 0);
          lcd.print("Fora do ");
          lcd.setCursor(3, 1);
          lcd.print("Horario");
          delay(2000);
          respondeu = true;
          break;
        } 
        else if (ver_horario == 'h') {
          lcd.clear();
          lcd.setCursor(2, 0);
          lcd.print("Liberado:");
          lcd.setCursor(3, 1);
          lcd.print("Bem Vindo");
          delay(2000);
          respondeu = true;
          break;
        }
      }
    }

    if (!respondeu) {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Erro Comunicacao");
        lcd.setCursor(0, 1);
        lcd.print("Python n respondeu");
        delay(2000);
    }
    
    lcd.clear();
    
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_NOTFOUND) {
    lcd.clear();
    lcd.setCursor(2, 0);
    lcd.print("Nao Cadastrado");
    delay(2000);
    lcd.clear();
    return p;
  }

  return p;
}

uint8_t deleteFinger(uint8_t id){
    uint8_t p = -1;

  p = finger.deleteModel(id);

  if (p == FINGERPRINT_OK) {
    lcd.clear();
    lcd.setCursor(2,0);
    lcd.print("Deletado!!");
    delay(3000);
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    lcd.setCursor(2, 0);
    lcd.print("Houve algum");
    lcd.setCursor(3, 1);
    lcd.print("Erro!!");
    delay(3000);
  } else if (p == FINGERPRINT_BADLOCATION) {
    lcd.setCursor(2, 0);
    lcd.print("Houve algum");
    lcd.setCursor(3, 1);
    lcd.print("Erro!!");
    delay(3000);
  } else if (p == FINGERPRINT_FLASHERR) {
    lcd.setCursor(2, 0);
    lcd.print("Houve algum");
    lcd.setCursor(3, 1);
    lcd.print("Erro!!");
    delay(3000);
  } else {
    Serial.print("Unknown error: 0x"); Serial.println(p, HEX);
  }
  
  return p && true;
}

