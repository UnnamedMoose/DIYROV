#include "BrushlessDCMotor.h"

// Method definitions.
BrushlessDCMotor::BrushlessDCMotor
(
	const char* motorID,
	int maximumThrustValue,
	int maximumEnginePulseWidth,
	int minimumEnginePulseWidth,
	int armEnginePulseWidth,
	int motorPinInput,
	int relayPinInput
)
:
Module(motorID),
currentPulseWidth(0), // Ditto - zero thrust.
maxThrustValue(maximumThrustValue),
maxPulseWidth(maximumEnginePulseWidth),
minPulseWidth(minimumEnginePulseWidth),
armPulseWidth(armEnginePulseWidth),
reversedThrust(false), // By default the thrust isn't reversed.
motorPin(motorPinInput),
relayPin(relayPinInput)
/* BrushlessDCMotor contructor. Initialise all the class fields, do nothing else.
 * 
 * @param motorID - int that is a unique number used to distinguish all the
 * 	motors connected to the Arduino.
 * @param maximumThrustValue - maximum value of the desired thrust that will be
 * 	supplied to this class. Used to scale the desired thrust to the pulse width.
 * @param minPulseWidth,maxPulseWidth - the range of the pusle widths accepted
 * 	by the used electronic speed controller, in microseconds.
 * @param motorPinInput - Arduino pin to which the motor is connected.
 * @param relayPinInput - Arduino pin to which the relay is connected. The relay
 * 	is used to reverse the thrust of the engine.
 */
{
	pinMode(relayPin,OUTPUT); // We will only flick the relay, so it's a simple output pin.
}	

BrushlessDCMotor::BrushlessDCMotor
(
	const char* motorID,
	int motorPinInput,
	int relayPinInput
)
:
Module(motorID),
currentPulseWidth(-1), // Ditto - zero thrust.
maxThrustValue(-1),
maxPulseWidth(-1),
minPulseWidth(-1),
reversedThrust(false), // By default the thrust isn't reversed.
motorPin(motorPinInput),
relayPin(relayPinInput)
/* BrushlessDCMotor contructor. Initialise the class fields corresponding
 * to the motorIndentifier integer, as well as the Arudino pins that the motor
 * and a relay (used to reverse thrust) are connected to. All the remaining 
 * class fields are initialised with invlaid values to make sure errors are
 * thrown when someone uses fields without consciously setting their values
 * using setRelayPin, setMotorPin, setThrustValueRange and setPulseWidthRnage
 * methods (pins should be set before the ranges).
 * 
 * @param motorID - int that is a unique number used to distinguish all the
 * 	motors connected to the Arduino.
 * @param motorPinInput - Arduino pin to which the motor is connected.
 * @param relayPinInput - Arduino pin to which the relay is connected. The relay
 * 	is used to reverse the thrust of the engine.
 */
{
	// Can't attach to a servo yet because we don't know the range of pulse widths; this will be done when arming the motor anyway.
	pinMode(relayPin,OUTPUT); // We will only flick the relay, so it's a simple output pin.
}

BrushlessDCMotor::BrushlessDCMotor()
:
currentPulseWidth(-1), // Zero thrust.
maxThrustValue(-1),
maxPulseWidth(-1),
minPulseWidth(-1),
reversedThrust(false), // By default the thrust isn't reversed.
motorPin(-1),
relayPin(-1)
/* Default contructor, initialise all the class fields with invlaid values to
 * make sure errors are thrown when someone uses fields without consciously
 * setting their values using setRelayPin, setMotorPin, setThrustValueRange and
 * setPulseWidthRnage methods (pins should be set before the ranges).
 */
{
}

void BrushlessDCMotor::setThrustValueRange(int maximumThrustValue)
/* Set the maxThrustValue and minThrustValue class fields that describe the
 * range of the currentValue that will be translated to engine thrust.
 *
 * @param maximumThrustValue - maximum of the thrust values that will be
 * 	provided to this BrushlessDCMotor.
 */
{
	maxThrustValue=maximumThrustValue;
}

void BrushlessDCMotor::setPulseWidthRange(int maximumEnginePulseWidth, int minimumEnginePulseWidth)
/* Set the maxPulseWidth and maxPulseWidth class fields that describe the
 * range of the pulse widths translate to engine thrust (brushless motor's thrust
 * is described by the width of the pulse in the pulse width modulation). These
 * fields are specific to the electronic speed controller (ESC) used to drive
 * the motor.
 *
 * @param maximumEnginePulseWidth,minimumEnginePulseWidth - range of the pulse
 * 	widths that correspond to maximum and minimum RPMs of this motor. In microseconds.
 */
{
	minPulseWidth=minimumEnginePulseWidth;
	maxPulseWidth=maximumEnginePulseWidth;
}

void BrushlessDCMotor::setMotorPin(int motorPinInput)
/* Set the motorPin class field that says which pin on the Arduino the motor is
 * physically connected to. setPulseWidthRange method should be called after
 * this one to create the pulse width modulation interface.
 */
{
	motorPin=motorPinInput;
	// Can't attach the Servo class yet, we don't know the range of pulse widths. This will be handled in setPulseWidthRange method.
}

void BrushlessDCMotor::setRelayPin(int relayPinInput)
/* Set the relayPin class field that says which pin on the Arduino the relay is
 * physically connected to. This relay is used to reverse the thrust of the engine
 * by reversing the direction of the current flow through it. Also set the relayPin
 * as output.
 */
{
	relayPin=relayPinInput;
	pinMode(relayPin,OUTPUT); // We will only flick the relay, so it's a simple output pin.
}

void BrushlessDCMotor::setValue(int newThrust)
/* Set the throttle of the engine to the desired value. This is achieved by setting
 * the width of the pulse on the motorPin to the appropriate value by scaling
 * newThrust, which has to be between 0 and maxThrustValue,
 * to the pulse width, bound by minPulseWidth and maxPulseWidth.
 * 
 * If newThrust is negative, the direction of the thrust will be reversed by
 * reversing the direction of current flow through the motor by using a relay.
 * 
 * @param newThrust - a value between 0 and maxThrustValue that will be
 * 	scaled to the pusle width between minPulseWidth and	maxPulseWidth class
 * 	attributes. newThrust can be negative to indicate reverse thrust direction.
 */
{//TODO: when reversing thrust go through the zero throttle position to avoid burning shit.
	if(newThrust<0){ // < 0, if we set thrust to 0 make sure we're working forward again, it is likely we will go reverse->0->forward.
		reversedThrust=true; // Keep track of the fact we're working backwards.
		digitalWrite(relayPin,HIGH); // Flick the relay.
	}
	else // Go back to normal thrust direction.
	{
		reversedThrust=false;
		digitalWrite(relayPin,LOW);
	}
	
	currentValue=newThrust;
	currentPulseWidth = int( minPulseWidth + abs(currentValue)/double(maxThrustValue) * (maxPulseWidth-minPulseWidth) ); // Scale the desired throttle to pulse width and change to an int, as expected by the Servo class.
	#ifdef DEBUG_PRINTOUT
		Serial.print("    Setting pulse width for motor ");Serial.print(identifier);Serial.print( " to ");Serial.println( String(currentPulseWidth) );
	#endif
	
	motor.writeMicroseconds(currentPulseWidth);
}

void BrushlessDCMotor::setPulseWidth(int pulseWidth)
/* Manually set the pulse width of the engine.
 * 
 * @param pulseWidth - desired pulse width in microseconds.
 */
{
 	motor.writeMicroseconds(pulseWidth);
}
 
BrushlessDCMotor::~BrushlessDCMotor(void){}; // Do nothing special here.

int BrushlessDCMotor::arm(void)
/* Attach the motor to the chosen pins with the specified characteristics, i.e.
 * minimum and maximum pulse widths. Also set the arming pulse and request
 * the necessary delay from the overseer setup() function in main.
 */
{
	motor.attach(motorPin,minPulseWidth,maxPulseWidth);
	setPulseWidth(armPulseWidth);
	#ifdef DEBUG_PRINTOUT
		Serial.print("Armed motor: ");
		Serial.println(identifier);
	#endif
	return 25000;
}



