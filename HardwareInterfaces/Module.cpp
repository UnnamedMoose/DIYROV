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
	Serial.begin(serialBaudRate); // Start serial comms.
}
 
Module::Module(const char* newIdentifier)
/* Initialise this instance of the Module.
 */
{
	identifier = newIdentifier;
	currentValue = 0;
	Serial.begin(serialBaudRate); // Start serial comms.
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

int Module::arm(void)
/* Method encompassing setup of the module, i.e. the block of code called
 * during setup() in the main routine
 * 
 * @return - the delay required for the module to finish preparing
 */
{
// Do nothing by default.
	return 0;
}

const char* Module::getIdentifier(void)
/* Get the identifer of this Module. */
{
	return identifier;
}
