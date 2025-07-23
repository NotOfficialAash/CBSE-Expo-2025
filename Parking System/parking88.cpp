#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define OLED_WIDTH 128
#define OLED_HEIGHT 64

#define IR_FRONT 2
#define IR_LEFT 3
#define IR_RIGHT 4

#define ISD1820_PLAY_PIN 8

bool played = false;

Adafruit_SSD1306 display(OLED_WIDTH, OLED_HEIGHT, &Wire, -1);

void setup() {
  pinMode(IR_FRONT, INPUT);
  pinMode(IR_LEFT, INPUT);
  pinMode(IR_RIGHT, INPUT);
  pinMode(ISD1820_PLAY_PIN, OUTPUT);
  digitalWrite(ISD1820_PLAY_PIN, LOW);

  Serial.begin(9600);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED failed");
    while (1);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
}

void loop() {
  bool carPresent = digitalRead(IR_FRONT) == LOW;
  bool left = digitalRead(IR_LEFT) == LOW;
  bool right = digitalRead(IR_RIGHT) == LOW;

  display.clearDisplay();
  display.setCursor(0, 10);

  if (!carPresent) {
    display.println("Slot: Vacant");
    played = false;
  } else {
    if (left && right) {
      display.println("Parked Properly");
      played = false;
    } else {
      display.println("Misaligned!");
      if (!played) {
        // Trigger ISD1820 to play
        digitalWrite(ISD1820_PLAY_PIN, HIGH);
        delay(100); // Short pulse
        digitalWrite(ISD1820_PLAY_PIN, LOW);
        played = true;
      }
    }
  }

  display.display();
  delay(500);
}
