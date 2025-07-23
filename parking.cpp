const int irSensors[3] = {2, 3, 4};   // IR sensors
const int buzzer = 5;                // Buzzer pin

const int slotPaths[3][3] = {
  {6, 7, 8},     // LEDs for Slot 1
  {9, 10, 11},   // LEDs for Slot 2
  {12, A0, A1}   // LEDs for Slot 3
};

int lastState[3] = {HIGH, HIGH, HIGH};

void setup() {
  Serial.begin(9600);
  pinMode(buzzer, OUTPUT);

  for (int i = 0; i < 3; i++) {
    pinMode(irSensors[i], INPUT);
    for (int j = 0; j < 3; j++) {
      pinMode(slotPaths[i][j], OUTPUT);
    }
  }
}

void loop() {
  int foundFree = -1;

  for (int i = 0; i < 3; i++) {
    int currentState = digitalRead(irSensors[i]);

    // Detect change
    if (currentState != lastState[i]) {
      beepOnce();
      lastState[i] = currentState;
    }

    if (foundFree == -1 && currentState == HIGH) {
      foundFree = i;
    }
  }

 // Update LED pathways for the first available slot
for (int i = 0; i < 3; i++) {
  bool isFree = (i == foundFree && lastState[i] == HIGH);
  for (int j = 0; j < 3; j++) {
    digitalWrite(slotPaths[i][j], isFree ? HIGH : LOW);
  }
}


  // Send to Python: 1,0,1
  Serial.print(lastState[0]);
  Serial.print(",");
  Serial.print(lastState[1]);
  Serial.print(",");
  Serial.println(lastState[2]);

  delay(300);
}

void beepOnce() {
  digitalWrite(buzzer, HIGH);
  delay(1000);
  digitalWrite(buzzer, LOW);
}
