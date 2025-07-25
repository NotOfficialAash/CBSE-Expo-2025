int redPin = 8;
int yellowPin = 9;
int greenPin = 10;
int rainPin = 2;
bool isRaining;

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(yellowPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(rainPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  isRaining = digitalRead(rainPin) == LOW;  // LOW = rain detected
  Serial.println(isRaining);  // Send to Python

  if (Serial.available()) {
    char command = Serial.read();

    // Turn off all LEDs first
    digitalWrite(redPin, LOW);
    digitalWrite(yellowPin, LOW);
    digitalWrite(greenPin, LOW);

    // Turn on based on received command
    if (command == 'R') digitalWrite(redPin, HIGH);
    else if (command == 'Y') digitalWrite(yellowPin, HIGH);
    else if (command == 'G') digitalWrite(greenPin, HIGH);
  }

  delay(100);

  if (isRaining == 1) {
    Serial.println("It is raining");

  }
}
