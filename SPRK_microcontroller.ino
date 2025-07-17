#include <LiquidCrystal.h> 
#include "Servo.h" 
LiquidCrystal lcd( 2 , 3 , 4  , 5 , 6 , 7 ) ; 
#define pwm 9 
void device_controller();
Servo myServo; 

boolean fire=false; 
boolean smoke=false; 
boolean ldr=false; 
int err=0;
int m=0;
int angle;

const int trigPin =A2;      // trig pin of HC-SR04 
const int echoPin = A5;     // Echo pin of HC-SR04 
const int servoPin = 8;
int sensorPin = A0; //for temperature sensor
int gasPin = A1;//for smoke sensor
//int sensorPin3 = A4 
int tempsensor = A4 ;//for dc MOTOR
int sensorPin1_val = 0; 
int sensorPin2_val = 0; 
int sensorPin3_val = 0; 
//int buzzer = 13; 
int R_led = 10; 
int G_led = 13; 
int B_led = 12; 
int Y_led = 11; 
int dc2=A0;
int dc7=A3; // digital pin 14
//int dc1=13;
int read_value1; // variable for reading the sensorpin status 
int read_value2; 
int read_value3; 
bool alreadySent = false;
long duration, distance;


void setup() {
  Serial.begin(9600);
  //pinMode(dc1, OUTPUT); 
  pinMode(dc2, OUTPUT);
  pinMode(dc7, OUTPUT);
  delay(1000);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  myServo.attach(servoPin);
  myServo.write(90);
  pinMode(pwm, OUTPUT);
  digitalWrite(pwm, LOW);  
  lcd.begin(16, 2);
  lcd.clear() ; 
  lcd.setCursor ( 0,0 ) ; 
  lcd.print("      WELCOME"); 
  lcd.setCursor ( 0,1 ) ; 
  lcd.print("      home "); 
  delay ( 2000 ) ; 
        
    }



void loop() {

 if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    int len = command.length() + 1; // +1 for the null terminator
    char charArray[len];
    command.toCharArray(charArray, len);
    for (char c : charArray){
    m = device_controller(c);
    if (m == -1)
    err=1;
    }
    if(err==0)
      Serial.println("2");
    else {
      Serial.println("4");
      err=0;
    }
}

}
int device_controller(char device)
{
    switch(device)
    {
      case 'B':
      // turn on tv
        {lcd.clear() ; 
        lcd.setCursor ( 0,0 ) ; 
        lcd.print("   TV"); 
        lcd.setCursor ( 0,1 ) ; 
        lcd.print("      ON "); 
        delay ( 2000 ) ; 
        break;}
      case 'C':
      // turn off tv
      {lcd.clear() ; 
        lcd.setCursor ( 0,0 ) ; 
        lcd.print("   TV"); 
        lcd.setCursor ( 0,1 ) ; 
        lcd.print("    OFF "); 
        delay ( 2000 ) ; 
        lcd.clear() ; 
        break;}
      case 'D': // FAN ON with ULTRASONIC + SERVO
      {
        //ULTRASONIC 
        digitalWrite(trigPin, LOW);
        delayMicroseconds(2);
        digitalWrite(trigPin, HIGH);
        delayMicroseconds(10);
        digitalWrite(trigPin, LOW);

        // SERVO MOTOR
        duration = pulseIn(echoPin, HIGH);
        distance = duration * 0.034 / 2;  
        // WRITING ON LCD
        lcd.clear() ; 
        lcd.setCursor ( 0,0 ) ; 
        lcd.print("Distance: ");
        lcd.setCursor ( 0,1 ) ;
        lcd.print(distance);
        lcd.println(" cm");

         if (distance >= 5 && distance <= 100) {
        angle = map(distance, 5, 100, 150, 30);
        myServo.write(angle);
        }
        //FAN
        digitalWrite(pwm, HIGH); 
        break;
      }
      case 'E':
      //turn fan off
      {
        digitalWrite(pwm,LOW); 
        break;
      }
        case 'F': // Read and display Gas sensor (MQ-9)
      {
        int gasValue = analogRead(gasPin);
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Gas Level:");
        lcd.setCursor(0, 1);
        lcd.print(gasValue);
        delay(2000);

        if (gasValue > 400) {
          Serial.println("GAS_DETECTED");
   //       digitalWrite(buzzer, HIGH);
          lcd.clear();
          lcd.print("!! GAS ALERT !!");
          delay(2000);
        } 
        break;
      }
      case 'G': // Read and display temperature (LM35)
      {
        int analogValue = analogRead(tempsensor);
        float voltage = analogValue * (5.0 / 1023.0);
        float temperatureC = voltage * 100.0;
        Serial.print("TEMP:");
        Serial.println(temperatureC);
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Temp:");
        lcd.setCursor(0, 1);
        lcd.print(temperatureC);
        lcd.print(" C");
        delay(2000);
        break;
      }
      case 'H': //start dc motor
      {
        // Move motor forward
        digitalWrite(dc2, HIGH);
        digitalWrite(dc7, LOW);
        //analogWrite(dc1, 150);  // Speed (0-255)
        delay(2000);

        // Stop motor
        digitalWrite(dc2, LOW);
        digitalWrite(dc7, LOW);
        delay(1000);

        // Move motor backward
        digitalWrite(dc2, LOW);
        digitalWrite(dc7, HIGH);
        //analogWrite(dc1, 150);  // Speed (0-255)
        delay(2000);
        break;
      }
      case 'I': //stop dc motor
      {
        // Stop motor
        digitalWrite(dc2, LOW);
        digitalWrite(dc7, LOW);
        delay(1000);
        break;
      }
      case 'J': //turn room1 light oN
      {
        digitalWrite(B_led, LOW);
        delay(1000);
        break;
      }
      case 'K': //turn room1 light oFF
      {
        digitalWrite(B_led, LOW);
        delay(1000);
        break;
      }
      case 'L': //turn room2 light oN
      {
        digitalWrite(Y_led, HIGH);
        delay(1000);
        break;
      }
      case 'M': //turn room2 light oFF
      {
        digitalWrite(Y_led, LOW);
        delay(1000);
        break;
      }
      case 'N': //turn kitchen light oN
      {
        digitalWrite(G_led, HIGH);
        delay(1000);
        break;
      }
      case 'O': //turn kitchen light oFF
      {
        digitalWrite(G_led, LOW);
        delay(1000);
        break;
      }
      case 'P': //turn bathroom light oN
      {
        digitalWrite(R_led, HIGH);
        delay(1000);
        break;
      }
      case 'Q': //turn bathroom light oFF
      {
        digitalWrite(R_led, LOW);
        delay(1000);
        break;
      }
      default:
      {
          return -1;
      }
    }
}


