#include <LiquidCrystal.h>

// Pins: RS, E, D4, D5, D6, D7
LiquidCrystal lcd(5, 6, 7, 8, 9, 10);

// IR sensors
const int ir1 = 2;
const int ir2 = 3;
const int ir3 = 4;

void setup() {
  pinMode(ir1, INPUT);
  pinMode(ir2, INPUT);
  pinMode(ir3, INPUT);

  lcd.begin(16, 2);
  lcd.print("Smart Parking");
  delay(2000);
  lcd.clear();
}

void loop() {
  bool s1 = digitalRead(ir1);
  bool s2 = digitalRead(ir2);
  bool s3 = digitalRead(ir3);

  int free = (s1 == HIGH) + (s2 == HIGH) + (s3 == HIGH);

  lcd.setCursor(0, 0);
  lcd.print("Free: ");
  lcd.print(free);
  lcd.print("    "); // clear extra

  lcd.setCursor(0, 1);
  lcd.print("S1:");
  lcd.print(s1 == HIGH ? "F " : "X ");
  lcd.print("S2:");
  lcd.print(s2 == HIGH ? "F " : "X ");
  lcd.print("S3:");
  lcd.print(s3 == HIGH ? "F" : "X ");
  
  delay(1000);
}
