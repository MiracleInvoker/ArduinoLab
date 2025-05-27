#include <Arduino.h>


const int ledPIN = 9;

int fadeAmount = 8;
int brightness = 0;


void setup() {
	pinMode(ledPIN, OUTPUT);
}


void loop() {
	analogWrite(ledPIN, brightness);

	brightness = brightness + fadeAmount;

	if (brightness <= 0 || brightness >= 255) {
		fadeAmount = -fadeAmount;
	}

	delay(30);
}
