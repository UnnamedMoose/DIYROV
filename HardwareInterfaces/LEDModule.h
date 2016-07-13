/* A class that serves as an interface between an Arduino and a LED lamp.
 *
 * This header and the source have to be placed in the Arduino libraries' directory,
 * e.g. /usr/share/arduino/libraries/ in LEDModule folder.
 *
 * @author: Aleksander Lidtke
 * @email: aleksadner.lidtke@gmail.com
 * @url: www.aleksanderlidtke.com
 * @since: 10 Jul 2016
 * @version: 1.0.0
 * 
 * CHANGELOG
 * 10 Jul 2016 - 1.0.0 - Alek Lidtke - released the first version.
 */
#ifndef LEDMODULE_H
#define LEDMODULE_H

#include "Arduino.h" // Basic Arduino stuff.
#include "Module.h" // The base class of all the actuators and sensors.

class LEDModule : public Module
{
	private:
		int outputPin;
	public:
		LEDModule(const char* sensorID, int sensorOutputPin);
		LEDModule(void);
		~LEDModule(void);
		
		void setValue(int value); // override and set pin output
		void blink(int blinkDelay, int noBlinks); // blink a couple of times with a given interval
};

#endif
