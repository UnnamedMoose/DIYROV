#include "DepthSensor.h"

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
