#include <Arduino.h>
#include <Servo.h>


Servo myServo;

static constexpr uint8_t
    trigPIN = 9,
    echoPIN = 10,
    servoPIN = 11,
    buzzerPIN = 7,
    ledPIN = 4;

uint8_t angle = 0;
int8_t direction = 1;
uint16_t distance = 0;
uint16_t threshold_distance;
bool start = false;


static uint16_t getDistance() {
    // Trigger Pulse
    digitalWrite(trigPIN, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPIN, LOW);

    /*
    pulseIn() returns µs
    Speed of Sound ~343 m/s -> 0.0343 cm / µs
    Round 0.0343 ≈ 343/10000; divide by 2 for go - return
    */
    unsigned long micro_seconds = pulseIn(echoPIN, HIGH);

    return (uint16_t) ((micro_seconds * 343UL) / 20000UL);
}


static uint16_t getDistanceMedian() {
    uint16_t a = getDistance();
    uint16_t b = getDistance();
    uint16_t c = getDistance();

    if (a > b) { uint16_t t = a; a = b; b = t; }
    if (b > c) { uint16_t t = b; b = c; c = t; }
    if (a > b) { uint16_t t = a; a = b; b = t; }

    return b;
}


void setup() {
    Serial.begin(9600);
    myServo.attach(servoPIN);

    pinMode(trigPIN, OUTPUT);
    pinMode(echoPIN, INPUT);

    pinMode(buzzerPIN, OUTPUT);
    pinMode(ledPIN, OUTPUT);
}


void loop() {

    if (Serial.available() > 0) {
        String line = Serial.readStringUntil('\n');
        line.trim();

        uint8_t tmpBool;

        sscanf(line.c_str(), "%hhu,%u", &tmpBool, &threshold_distance);
        start = (tmpBool == 1);
    }

    if (start){
        myServo.write(angle);

        delay(30);

        distance = getDistanceMedian();

        // "angle,distance\n"
        Serial.print(angle);
        Serial.print(',');
        Serial.print(distance);
        Serial.print('\n');

        bool alert = (distance < threshold_distance && distance != 0);
        digitalWrite(buzzerPIN, alert);
        digitalWrite(ledPIN, alert);

        angle += direction;
        if (angle == 180 || angle == 0){
            direction = -1 * direction;
        }
    }
    else{
        digitalWrite(buzzerPIN, LOW);
        digitalWrite(ledPIN, LOW);
        myServo.write(0);
    }
}