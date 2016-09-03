/* A class that serves as an interface between an Arduino and a brushless DC
 * motor and a relay used to reverse the thrust of the engine by reversing the
 * direction of the current flow through it.
 *
 * This header and the source have to be placed in the Arduino libraries' directory,
 * e.g. /usr/share/arduino/libraries/ in BrushlessDCMotor folder.
 *
 * @author: Aleksander Lidtke
 * @email: aleksadner.lidtke@gmail.com
 * @url: www.aleksanderlidtke.com
 * @since: 26 Sep 2015
 * @version: 2.1.1
 * 
 * CHANGELOG
 *  5 Sep 2015 - 1.0.0 - Alek Lidtke - released the first version.
 * 	6 Sep 2015 - 2.0.0 - Alek & Artur Lidtke - derived this from the Module class.
 * 19 Sep 2015 - 2.1.0 - Alek & Artur Lidtke - created a decicated method to arm
 * 	the motors, attaching servos in the constructor doesn't work.
 * 26 Sep 2015 - 2.1.1 - Alek Lidtke - limited when the debugging messages will be printed.
 */
#ifndef BRUSHLESSDCMOTOR_H
#define BRUSHLESSDCMOTOR_H

#include "Arduino.h" // Basic Arduino stuff.
#include "Module.h" // The base class of all the actuators and sensors.
#include <Servo.h> // We need this to control the PWM Arduino pin.

class BrushlessDCMotor : public Module
{
	private:
		int currentPulseWidth, maxThrustValue;
		int maxPulseWidth, minPulseWidth, armPulseWidth;
		bool reversedThrust;
		int motorPin, relayPin;
	public:
		Servo motor;
		BrushlessDCMotor(const char* motorID, int maximumThrustValue, int maximumEnginePulseWidth, int minimumEnginePulseWidth, int armEnginePulseWidth, int motorPinInput, int relayPinInput);
		BrushlessDCMotor(const char* motorID, int motorPinInput, int relayPinInput);
		BrushlessDCMotor(void);
		~BrushlessDCMotor(void);
		
		void setThrustValueRange(int maximumThrustValue);
		void setPulseWidthRange(int maximumEnginePulseWidth, int minimumEnginePulseWidth);
		void setMotorPin(int motorPinInput);
		void setRelayPin(int relayPinInput);
		void setValue(int newThrust); // Override parent method.
		void setPulseWidth(int pulseWidth);
		int arm(); // Override the parent method.
};

#endif
