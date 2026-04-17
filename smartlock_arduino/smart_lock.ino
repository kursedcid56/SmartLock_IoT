##include <Arduino_FreeRTOS.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// --- CHÂN CẮM ---
#define RST_PIN    9
#define SS_PIN     10
#define SERVO_PIN  6
#define BUZZER_PIN 5
#define LED_XANH   4
#define LED_DO     3

MFRC522           mfrc522(SS_PIN, RST_PIN);
Servo             myServo;
LiquidCrystal_I2C lcd(0x27, 16, 2);

// --- BIẾN TOÀN CỤC ---
// 0=Chờ | 1=Mở | 2=Sai Thẻ | 3=Đang test | 4=Sai Giờ
volatile int trangThai = 0; 
int trangThaiCu = -1;
char lastUID[9] = ""; 

void capNhatLCD() {
  if (trangThai == trangThaiCu) return;  
  lcd.clear();
  switch (trangThai) {
    case 0:
      lcd.setCursor(0,0); lcd.print(F("San sang"));
      lcd.setCursor(0,1); lcd.print(F("Moi quet the..."));
      break;
    case 1:
      lcd.setCursor(0,0); lcd.print(F("Cua dang MO!"));
      lcd.setCursor(0,1); lcd.print(F("Vui long vao..."));
      break;
    case 2:
      lcd.setCursor(0,0); lcd.print(F("The SAI!"));
      lcd.setCursor(0,1); lcd.print(F("Chua dang ky"));
      break;
    case 3:
      lcd.setCursor(0,0); lcd.print(F("Dang kiem tra..."));
      lcd.setCursor(0,1); lcd.print(lastUID);
      break;
    case 4:
      lcd.setCursor(0,0); lcd.print(F("Tu choi vao!"));
      lcd.setCursor(0,1); lcd.print(F("Ngoai khung gio"));
      break;
    case 5:
      lcd.setCursor(0,0); lcd.print(F("THEM THE MOI OK!"));
      lcd.setCursor(0,1); lcd.print(F("Da luu Database "));
      break;  
    case 6:
      lcd.setCursor(0,0); lcd.print(F("Che do Them the:"));
      lcd.setCursor(0,1); lcd.print(F("Moi quet the..."));
      break;
    case 7: 
      lcd.setCursor(0,0); lcd.print(F("THE DA TON TAI!"));
      lcd.setCursor(0,1); lcd.print(F("Dung the khac..."));
      break;
    case 8: // TRẠNG THÁI 8: THẺ ĐANG BỊ KHÓA
      lcd.setCursor(0,0); lcd.print(F("THONG BAO:"));
      lcd.setCursor(0,1); lcd.print(F("THE DANG BI KHOA"));
      break;   
  }
  trangThaiCu = trangThai;
}
    
// =========================================================
// TASK 1: LẮNG NGHE LỆNH 
// =========================================================
void Task_Serial(void *pvParameters) {
  (void) pvParameters;
  vTaskDelay( 100 / portTICK_PERIOD_MS ); // Chờ hệ thống ổn định
  
  for (;;) {
    if (Serial.available() > 0) {
      char c = Serial.read();
      if (c == 'M' || c == 'm')      { trangThai = 1; } 
      else if (c == 'X' || c == 'x') { trangThai = 2; } 
      else if (c == 'T' || c == 't') { trangThai = 4; } 
      else if (c == 'S' || c == 's') { trangThai = 5; } 
      else if (c == 'L' || c == 'l') { trangThai = 6; } 
      else if (c == 'E' || c == 'e') { trangThai = 7; } // Báo thẻ đã tồn tại
      else if (c == 'K' || c == 'k') { trangThai = 8; } // Nhận lệnh báo thẻ bị khóa
    }
    vTaskDelay( 20 / portTICK_PERIOD_MS ); 
  }
}

// =========================================================
// TASK 2: QUÉT THẺ RFID
// =========================================================
void Task_RFID(void *pvParameters) {
  (void) pvParameters;
  vTaskDelay( 100 / portTICK_PERIOD_MS ); // Chờ hệ thống ổn định
  const char hex_chars[] = "0123456789ABCDEF"; 
  
  for (;;) {
    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
      
      digitalWrite(BUZZER_PIN, HIGH);
      vTaskDelay( 50 / portTICK_PERIOD_MS );
      digitalWrite(BUZZER_PIN, LOW);
        
      for (byte i = 0; i < mfrc522.uid.size; i++) {
        lastUID[i*2]     = hex_chars[mfrc522.uid.uidByte[i] >> 4]; //0*2 = 0(sodau);0*2+1=1(sothu2)
        lastUID[i*2 + 1] = hex_chars[mfrc522.uid.uidByte[i] & 0x0F];//1*2=2(sothu3);1*2+1=3(sothu4)
      }
      lastUID[mfrc522.uid.size * 2] = '\0'; 

      Serial.print(F("UID:"));
      Serial.println(lastUID);

      trangThai = 3; 

      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();
    }
    vTaskDelay( 100 / portTICK_PERIOD_MS ); 
  }
}

// =========================================================
// TASK 3: ĐIỀU KHIỂN CỬA 
// =========================================================
void Task_Action(void *pvParameters) {
  (void) pvParameters;
  vTaskDelay( 100 / portTICK_PERIOD_MS ); 
  
  int stateHienTai = -1;
  TickType_t thoiGianBatDauState = 0; 

  bool cuaDangMo = false;
  TickType_t thoiGianMoCua = 0;

  for (;;) {
    capNhatLCD(); 

    // 1. BẮT SỰ KIỆN THAY ĐỔI TRẠNG THÁI
    if (trangThai != stateHienTai) {
        stateHienTai = trangThai;
        thoiGianBatDauState = xTaskGetTickCount(); 

        if (stateHienTai == 1) { // MỞ CỬA
            cuaDangMo = true;
            thoiGianMoCua = xTaskGetTickCount();

            digitalWrite(LED_DO, LOW);
            digitalWrite(LED_XANH, HIGH);
            myServo.write(50);
            
            digitalWrite(BUZZER_PIN, HIGH);
            vTaskDelay( 200 / portTICK_PERIOD_MS );
            digitalWrite(BUZZER_PIN, LOW);
        }
        else if (stateHienTai == 0 && !cuaDangMo) { // VỀ TRẠNG THÁI CHỜ
            digitalWrite(LED_XANH, LOW);
            digitalWrite(LED_DO, HIGH);
            digitalWrite(BUZZER_PIN, LOW);
        }
    }

    // 2. LUỒNG TỰ ĐỘNG ĐÓNG CỬA (Sau 3 giây)
    if (cuaDangMo) {
        if ( (xTaskGetTickCount() - thoiGianMoCua) * portTICK_PERIOD_MS >= 3000 ) {
            myServo.write(0); 
            digitalWrite(LED_XANH, LOW);
            digitalWrite(LED_DO, HIGH);
            cuaDangMo = false; 

            if (trangThai == 1) trangThai = 0; 
        }
    }

    // 3. LUỒNG BÁO LỖI (Gộp trạng thái 2: Sai thẻ, 4: Sai giờ, 7: Thẻ đã tồn tại)
    // Đặc điểm: Kêu bíp bíp bíp nhanh trong 2 giây
    if (stateHienTai == 2 || stateHienTai == 4 || stateHienTai == 7) {
        long dt = (xTaskGetTickCount() - thoiGianBatDauState) * portTICK_PERIOD_MS;
        if (dt < 2000) {
            digitalWrite(BUZZER_PIN, (dt / 100) % 2 == 0); 
        } else {
            digitalWrite(BUZZER_PIN, LOW);
            trangThai = 0; 
        }
    }

    // 4. LUỒNG BÁO THẺ BỊ KHÓA (Trạng thái 8)
    // Đặc điểm: Kêu 1 tiếng "Títttt" dài 2 giây rồi tắt
    if (stateHienTai == 8) {
        long dt = (xTaskGetTickCount() - thoiGianBatDauState) * portTICK_PERIOD_MS;
        if (dt < 2000) {
            digitalWrite(BUZZER_PIN, HIGH);
        } else {
            digitalWrite(BUZZER_PIN, LOW);
            trangThai = 0; 
        }
    }

    // 5. LUỒNG LỖI MẠNG (Trạng thái 3)
    if (stateHienTai == 3) {
        if ( (xTaskGetTickCount() - thoiGianBatDauState) * portTICK_PERIOD_MS >= 3000 ) {
            lcd.clear();
            lcd.setCursor(0,0); lcd.print(F("Loi mang/Web off"));
            digitalWrite(BUZZER_PIN, HIGH); vTaskDelay(100/portTICK_PERIOD_MS); digitalWrite(BUZZER_PIN, LOW);
            vTaskDelay(2000/portTICK_PERIOD_MS);
            trangThai = 0;
        }
    }
    
    // 6. LUỒNG THÊM THẺ THÀNH CÔNG (Trạng thái 5)
    if (stateHienTai == 5) {
        long dt = (xTaskGetTickCount() - thoiGianBatDauState) * portTICK_PERIOD_MS;
        if (dt < 2000) { 
            if (dt < 600) digitalWrite(BUZZER_PIN, (dt / 100) % 2 == 0);
            else digitalWrite(BUZZER_PIN, LOW);
        } else {
            digitalWrite(BUZZER_PIN, LOW); 
            trangThai = 0; 
        }
    }

    // 7. LUỒNG CHỜ QUẸT THẺ ĐỂ THÊM (Trạng thái 6)
    if (stateHienTai == 6) {
        if ( (xTaskGetTickCount() - thoiGianBatDauState) * portTICK_PERIOD_MS >= 15000 ) {
            trangThai = 0; 
            digitalWrite(BUZZER_PIN, HIGH); vTaskDelay(50/portTICK_PERIOD_MS); digitalWrite(BUZZER_PIN, LOW);
        }
    }

    vTaskDelay( 50 / portTICK_PERIOD_MS );
  }
}

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();

  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_XANH,   OUTPUT);
  pinMode(LED_DO,     OUTPUT);

  myServo.attach(SERVO_PIN);
  myServo.write(0);
  digitalWrite(LED_DO, HIGH);

  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,0); lcd.print(F("Khoi dong..."));
  
  // KHỞI TẠO TASK (Đã tối ưu RAM)
  xTaskCreate(Task_RFID,   "RFID",   128, NULL, 1, NULL); 
  xTaskCreate(Task_Serial, "Serial", 128, NULL, 2, NULL); 
  xTaskCreate(Task_Action, "Action", 128, NULL, 3, NULL); 
}

void loop() { }
