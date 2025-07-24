#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// OLED configuration
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define OLED_ADDR     0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// IR sensors and LEDs for 3 slots
const int irPins[3] = {2, 3, 4};     // IR sensor digital pins
const int ledPins[3] = {6, 7, 8};    // Corresponding LED pins
const int buzzerPin = 10;            // Buzzer pin

int slotStatus[3] = {0, 0, 0};       // Current slot status: 0 = Free, 1 = Occupied
int prevStatus[3] = {0, 0, 0};       // To detect changes for buzzer trigger

void setup() {
  Serial.begin(9600);

  // Initialize OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;); // Loop forever if OLED init fails
  }

  display.clearDisplay();
  display.display();

  // Set pin modes
  for (int i = 0; i < 3; i++) {
    pinMode(irPins[i], INPUT);
    pinMode(ledPins[i], OUTPUT);
  }
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW); // Ensure buzzer is off initially
}

void loop() {
  int freeCount = 0;
  bool changeDetected = false;

  // Read IR sensors and update LEDs
  for (int i = 0; i < 3; i++) {
    int sensorValue = digitalRead(irPins[i]);

    if (sensorValue == LOW) {
      slotStatus[i] = 1; // Occupied
      digitalWrite(ledPins[i], HIGH);
    } else {
      slotStatus[i] = 0; // Free
      digitalWrite(ledPins[i], LOW);
      freeCount++;
    }

    // Detect entry/exit for buzzer
    if (slotStatus[i] != prevStatus[i]) {
      changeDetected = true;
      prevStatus[i] = slotStatus[i];
    }
  }

  // Activate buzzer for 1 second if a change occurred
  if (changeDetected) {
    digitalWrite(buzzerPin, HIGH);
    delay(1000);
    digitalWrite(buzzerPin, LOW);
  }

  // Display parking info on OLED
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Parking Slot Status:");

  for (int i = 0; i < 3; i++) {
    display.setCursor(0, 14 + i * 12); // spacing lines
    display.print("Slot ");
    display.print(i + 1);
    display.print(": ");
    display.println(slotStatus[i] ? "Occupied" : "Free");
  }

  display.setCursor(0, 54);
  display.print("Free slots: ");
  display.print(freeCount);

  display.setCursor(80, 0);
  display.print(freeCount == 0 ? "FULL" : "WELCOME");

  display.display();
  delay(500); // Update interval
}
