/* A class that serves as an interface between and Arduino and a brushless DC
 * motor and a relay used to reverse the thrust of the engine by reversing the
 * direction of the current flow through it.
 *
 * This header and the source have to be placed in the Arduino libraries' directory,
 * e.g. /usr/share/arduino/libraries/ in BrushlessDCMotor folder.
 *
 * @author: Aleksander Lidtke
 * @email: aleksadner.lidtke@gmail.com
 * @url: www.aleksanderlidtke.com
 * @since:  5 Sep 2015
 * @version: 1.0.0
 * 
 * CHANGELOG
 *  5 Sep 2015 - 1.0.0 - Alek Lidtke - released the first version.
 */
#include "Arduino.h" // Basic Arduino stuff.
#include <Servo.h> // We need this to control the PWM Arduino pin.

class BrushlessDCMotor
{
	private:
		int currentThrustValue, currentPulseWidth, maxThrustValue;
		int maxPulseWidth, minPulseWidth;
		int motorIdentifier, motorPin, relayPin;
		Servo motor;
		bool reversedThrust;
	public:
		BrushlessDCMotor(int motorID, int motorPinInput, int maximumThrustValue, int maximumEnginePulseWidth, int minimumEnginePulseWidth, int relayPinInput);
		BrushlessDCMotor(int motorID, int motorPinInput, int relayPinInput);
		BrushlessDCMotor(void);
		~BrushlessDCMotor(void);
		
		void setThrustValueRange(int maximumThrustValue);
		void setPulseWidthRange(int maximumEnginePulseWidth, int minimumEnginePulseWidth);
		void setMotorPin(int motorPinInput);
		void setRelayPin(int relayPinInput);
		void setThrust(int newThrust);
};
