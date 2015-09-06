/* A class that serves as an interface between an Arduino and a generic piece of 
 * equipment, e.g. a sensor or an actuator. Other specific classes used to control
 * e.g brushless DC motors, LEDs or depth sensors are derived from this class.
 *
 * This header and the source have to be placed in the Arduino libraries' directory,
 * e.g. /usr/share/arduino/libraries/ in Module folder.
 *
 * @author: Aleksander & Artur Lidtke
 * @email: aleksadner.lidtke@gmail.com
 * @url: www.aleksanderlidtke.com
 * @since:  6 Sep 2015
 * @version: 1.0.0
 * 
 * CHANGELOG
 *  6 Sep 2015 - 1.0.0 - Alek Lidtke - released the first version.
 */
#ifndef MODULE_H
#define MODULE_H

#include "Arduino.h" // Basic Arduino stuff.

class Module
{
	protected:
		const char* identifier;
		int currentValue;
	public:
		Module(void);
		Module(const char* newIdentifier);
		~Module(void);
		virtual void setValue(int newValue);
		int getValue(void);
		const char* getIdentifier(void);
		
		static const int serialBaudRate;
};

#endif
