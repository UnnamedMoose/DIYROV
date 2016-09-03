#include "LEDModule.h"

LEDModule::LEDModule(const char* sensorID, int sensorOutputPin)
:
Module(sensorID),
outputPin(sensorOutputPin)
/* Initialise the instance of this sensor that will turn the LED on or off by
 * toggling a pin high or low.
 * 
 * @param sensorID - name of this sensor that will be sent to the Arduino to get
 * 	its value.
 * @param sensorOutputPin - the pin to which the LEDs are attached.
 */
{
	pinMode(sensorOutputPin,OUTPUT);
}

LEDModule::LEDModule(void){}; // Do nothing special here.

LEDModule::~LEDModule(void){}; // Do nothing special here.

void LEDModule::setValue(int value)
/* Set the pin high or low to turn the LEDs on or off. If value==1 the LEDs are
 * turned on, if 0 they're turned off.
 */
{
	if(value==1)
	{
		digitalWrite(outputPin, HIGH);
	}
	else if(value==0)
	{
		digitalWrite(outputPin, LOW);
	}
}

void LEDModule::blink(int blinkDelay, int noBlinks)
/* Turn the LED on and off a number of times, wait for a given number of milliseconds
 * when the LEDs are on, and then the same amount of time before turning them 
 * back on.
 * @param blinkDelay - how many milliseconts to wait when the LEDs are on and off.
 * @param noBlinks - how many times to blink the LEDs.
 */
{
	for(int i=0;i<noBlinks;i++) // Turn the LEDs on, wait a while, and turn it off and wait again.
	{
		digitalWrite(outputPin, HIGH);
		delay(blinkDelay); // Keep the LED on for a while.
		digitalWrite(outputPin, LOW);
		delay(blinkDelay); // Wait before turning the LEDs back on.
	}
}
