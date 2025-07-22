const int ir1 = 2;
const int ir2 = 3;
const int ir3 = 4;

void setup() {
  pinMode(ir1, INPUT);
  pinMode(ir2, INPUT);
  pinMode(ir3, INPUT);
  
  Serial.begin(9600);
  delay(2000);
}

void loop() {
  bool s1 = digitalRead(ir1);
  bool s2 = digitalRead(ir2);
  bool s3 = digitalRead(ir3);

  // Format: "s1,s2,s3"
  Serial.print(s1);
  Serial.print(",");
  Serial.print(s2);
  Serial.print(",");
  Serial.println(s3);
  
  delay(1000);
}