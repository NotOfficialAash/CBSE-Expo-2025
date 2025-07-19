const int LED_PIN = 13; // Example: built-in LED on pin 13

void setup() {
  Serial.begin(9600); // Initialize serial communication at 9600 baud
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n'); // Read incoming string until newline
      command.trim(); // Remove any leading/trailing whitespace
      if (command == "ON") {
        digitalWrite(LED_PIN, HIGH);
        Serial.println("LED ON");
      } else if (command == "OFF") {
        digitalWrite(LED_PIN, LOW);
        Serial.println("LED OFF");
      } else {
        Serial.println("Unknown command");
      }
    }
  }