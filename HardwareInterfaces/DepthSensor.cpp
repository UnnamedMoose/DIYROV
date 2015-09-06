/* A class that serves as an interface between an Arduino and a pressure sensor,
 * readings of which will be converted into depth.
 *
 * This header and the source have to be placed in the Arduino libraries' directory,
 * e.g. /usr/share/arduino/libraries/ in DepthSensor folder.
 *
 * @author: Aleksander Lidtke
 * @email: aleksadner.lidtke@gmail.com
 * @url: www.aleksanderlidtke.com
 * @since:  6 Sep 2015
 * @version: 1.0.0
 * 
 * CHANGELOG
 *  6 Sep 2015 - 1.0.0 - Alek Lidtke - released the first version.
 */

#include "DepthSensor.h" // Basic Arduino stuff.

DepthSensor::DepthSensor(const char* sensorID, int sensorInputPin)
:
Module(sensorID),
sensorPin(sensorInputPin)
/* Initialise the instance of this sensor that will read static pressure head
 * and convert it to depth measurements.
 * 
 * @param sensorID - name of this sensor that will be sent to the Arduino to get
 * 	its value.
 * @param sensorInputPin - the pin to which this sensor is attached.
 */
{
	pinMode(sensorPin,OUTPUT);
}

DepthSensor::DepthSensor(void){}; // Do nothing special here.

DepthSensor::~DepthSensor(void){}; // Do nothing special here.

int DepthSensor::getValue(void)
/* Get the reading from the sensor, convert it to depth, and return it.
 * 
 * @return - reading of the current depth in salt water in metres.
 */
{
	currentValue++;//TODO: get sensor reading here.
	return currentValue;
}
