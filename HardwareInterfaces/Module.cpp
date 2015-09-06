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
#include "Module.h"

// Initialise the static members.
const int Module::serialBaudRate = 19200; // Have to repeat const int in initialisation, for some reason.

Module::Module(void)
/* Default constructor, initialises all the fields with clearly default values
 * that will throw errors when they are used without conscious setting.
 */
{
	identifier = "UNKNOWN_MODULE";
	currentValue = 0;
}
 
Module::Module(const char* newIdentifier)
/* Initialise this instance of the Module.
 */
{
	identifier = newIdentifier;
	currentValue = 0;
}

Module::~Module(void){};/* Do nothing special here.*/

void Module::setValue(int newValue)
/* Set the current value for this piece of equipment. If it's an actuator it
 * will set e.g. the motor throttle to the desired value.
 *
 * N.B. it will also override the current sensor value, so be careful and don't
 * use it on sensors!
 *
 * @param newValue - the value to override the currentValue field with.
 */
{
	currentValue = newValue;
}

int Module::getValue(void)
/* Get the currentValue held by this instance, e.g. sensor reading or the intended
 * actuator value, say engine thrust.
 *
 * @return - the currently held value of the module.
 */
{
	return currentValue;
}

const char* Module::getIdentifier(void)
/* Get the identifer of this Module. */
{
	return identifier;
}