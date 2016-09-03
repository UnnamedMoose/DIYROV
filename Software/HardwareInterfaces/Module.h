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
 * @since: 26 Sep 2015
 * @version: 1.0.1
 * 
 * CHANGELOG
 *  6 Sep 2015 - 1.0.0 - Alek Lidtke - released the first version.
 * 26 Sep 2015 - 1.0.1 - Alek Lidtke - started to return 0 in the arm method by default - now we use Modules directly to parse SW commands so need to call this method and return something meaningful.
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
		// Sets control value of the module, e.g. thrust.
		virtual void setValue(int newValue);
		// Returns the current control value, e.g. sensor reading.
		virtual int getValue(void);
		// Method encompassing setup of the module, i.e. the block of code called
		// during setup() in the main routine; returns the delay required for the
		// module to finish preparing
		virtual int arm(void);
		// Returns the name of the module.
		const char* getIdentifier(void);
		
		// Serial frequency common for all modules.
		static const int serialBaudRate;
};

#endif
