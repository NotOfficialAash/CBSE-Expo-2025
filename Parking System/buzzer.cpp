const int slotSensors[] = {2, 3, 4}; // Pins connected to 3 IR sensors
const int totalSlots = 3;

const int buzzer = 5;

// Keep track of previous state for each slot
int lastState[totalSlots];

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < totalSlots; i++) {
    pinMode(slotSensors[i], INPUT);
    lastState[i] = digitalRead(slotSensors[i]); // Initialize state
  }

  pinMode(buzzer, OUTPUT);
  digitalWrite(buzzer, LOW);
}

void loop() {
  int freeSlots = 0;

  Serial.println("----- PARKING STATUS -----");

  for (int i = 0; i < totalSlots; i++) {
    int currentState = digitalRead(slotSensors[i]);

    // Display current slot status
    if (currentState == HIGH) {
      Serial.print("Slot ");
      Serial.print(i + 1);
      Serial.println(": Free");
      freeSlots++;
    } else {
      Serial.print("Slot ");
      Serial.print(i + 1);
      Serial.println(": Occupied");
    }

    // Check for change in state (entry or exit)
    if (currentState != lastState[i]) {
      if (currentState == LOW) {
        Serial.print("🔔 Car entered Slot ");
        Serial.println(i + 1);
      } else {
        Serial.print("🔔 Car exited Slot ");
        Serial.println(i + 1);
      }

      // Beep for 1 second
      digitalWrite(buzzer, HIGH);
      delay(1000);
      digitalWrite(buzzer, LOW);

      // Update last state
      lastState[i] = currentState;
    }
  }

  Serial.print("Total Free Slots: ");
  Serial.println(freeSlots);
  Serial.println("---------------------------");
  delay(500); // Small delay before next check
}
