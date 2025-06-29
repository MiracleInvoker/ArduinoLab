#include <Arduino.h>

const int buzzer_pin = 9;
const long baud_rate = 115200;

void setup() {
    pinMode(buzzer_pin, OUTPUT);

    /**
    --- Fast PWM Setup for Pin 9 and 10 (Timer1) ---
    This is a crucial step to improve audio quality.
    It changes the PWM frequency on pins 9 and 10 from the default ~490Hz to ~31.25kHz, which is outside the range of human hearing.
    This eliminates the low - frequency hum from the PWM itself.
    TCCR1A: WGM10 and WGM11 bits control waveform generation mode.
    TCCR1B: WGM12, WGM13 bits and CS10, CS11, CS12 bits control mode and clock prescaler.
    We are setting Timer1 to "8-bit Fast PWM" mode with no prescaler.
    **/

    TCCR1A = _BV(WGM10); // Set mode 5: 8-bit Fast PWM
    TCCR1B = _BV(WGM12) | _BV(CS10); // Set mode 5 and use a prescaler of 1

    // Start the serial Communication
    Serial.begin(baud_rate);
}

void loop() {
    if (Serial.available() > 0) {
        byte audioSample = Serial.read();

        analogWrite(buzzer_pin, audioSample);
    }
}