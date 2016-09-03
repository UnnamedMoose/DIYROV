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
#ifndef DEPTHSENSOR_H
#define DEPTHSENSOR_H

#include "Arduino.h" // Basic Arduino stuff.
#include "Module.h" // The base class of all the actuators and sensors.

class DepthSensor : public Module
{
	private:
		int sensorPin;
	public:
		DepthSensor(const char* sensorID, int sensorInputPin);
		DepthSensor(void);
		~DepthSensor(void);
		
		// FIXME this is a place-holder only, should use analogRead() and include a
		//	calibration section
		int getValue(void); // Override parent method.
};

#endif
