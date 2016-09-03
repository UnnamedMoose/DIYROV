/* A main application running on the Arduino that accepts telecommands from the
 * PC sent over serial, interprets them, conducts the required actions and sends
 * the required data back.
 * 
 * The telecommands follow a specified, custom protocol with a special character
 * at the beginning and end of every command. Every command can have a number of
 * strings that identify actions, followed by values (arguments for the actions).
 *
 * @author: Aleksander Lidtke
 * @email: alekasdner.lidtke@gmail.com
 * @url: www.aleksanderlidtke.com
 * @since: 10 Jul 2016
 * @version: 2.2.0
 */

//#define DEBUG_PRINTOUT // this will cause issues with arming modules as the GUI expects a delay in ms to be returned upon sending "armModules,1"; either fix or don't use the GUI in conjuction with this flag

// Custom includes.
#include "Module.h"
#include "BrushlessDCMotor.h"
#include "DepthSensor.h"
#include "Servo.h"
#include "LEDModule.h"

// Standard C/C++ includes
#include <stdio.h>

// ROV identifiers.
const String ROV_MODEL = "ROVing Drone";
const String ROV_SW_VERSION = "2.2.0r";

/* =============================================================================
 * FUNCTION DECLARATIONS.
 * =============================================================================
 */
void parseInput(void);
boolean getSerial(void);
void sendSensorReadings(void);
void armModules(void);
void armActuator(int idx);

/* =============================================================================
 * MOTOR DEFINITIONS.
 * =============================================================================
 */
// These values correspond to the currently selected electronic speed controller (ESC) - Turningy EA-25a.
#define MOTOR_ARM_PULSE_WIDTH 1100 // Pulse width in microseconds corresponding to zero throttle; used to arm the motors.
#define MOTOR_MAX_PULSE_WIDTH 2200 // Maximum pulse width of the motor in microseconds.
#define MOTOR_MIN_PULSE_WIDTH 800 // Minimum pulse width of the motor.
#define THROTTLE_STEPS 100 // How many levels of throttle we want to have.

// Pins are pairs of close-by pins with PWM and digital ones.
BrushlessDCMotor engine1 = BrushlessDCMotor("motorPortHor", THROTTLE_STEPS, MOTOR_MAX_PULSE_WIDTH,
	MOTOR_MIN_PULSE_WIDTH, MOTOR_ARM_PULSE_WIDTH, 3, 2); // orange // 1st-pwm, 2nd-digital
BrushlessDCMotor engine2 = BrushlessDCMotor("motorStbdHor", THROTTLE_STEPS, MOTOR_MAX_PULSE_WIDTH,
	MOTOR_MIN_PULSE_WIDTH, MOTOR_ARM_PULSE_WIDTH, 5, 4); // green
BrushlessDCMotor engine3 = BrushlessDCMotor("motorPortVer", THROTTLE_STEPS,MOTOR_MAX_PULSE_WIDTH,
	MOTOR_MIN_PULSE_WIDTH, MOTOR_ARM_PULSE_WIDTH, 6, 7); // white
BrushlessDCMotor engine4 = BrushlessDCMotor("motorStbdVer", THROTTLE_STEPS,
	2050, 950, 1200, 9, 8); // blue

/* =============================================================================
 * MISC ACTUATOR AND COMMAND DEFINITIONS.
 * =============================================================================
 */
Module armModulesModule = Module("armModules"); // Arms all the sensors and actuators.
Module armActuatorModule = Module("armActuator"); // Arms only one of the actuators depending on the argument it receives.

Module sendSensorReadingsModule = Module("sendSensorReadings"); // Sends sensor readings over serial.

Module refreshRate = Module("refreshRate"); // Changes the delay in the main loop.

LEDModule forwardLED = LEDModule("forwardLED", 12); // Switches the forward illumination LED, on pin 12, on or of.

const int ON_LED_PIN = 13; // LED on the Arduino board that will be lit when the ROV is in the main loop.

/* =============================================================================
 * SENSOR DEFINITIONS.
 * =============================================================================
 */
// TODO depth sensor plugged in to analog A0 pin
DepthSensor depthSensor = DepthSensor("depthReading",15); // For now a mock sensor.
DepthSensor depthSensor2 = DepthSensor("depthReading2",16); // Another mock sensor to make sure the message concatenation works well.

/* =============================================================================
 * TELECOMMAND PROTOCOL DEFINITION.
 * =============================================================================
 */
// Input and output data buffers.
#define DATABUFFERSIZE 180
char inputDataBuffer[DATABUFFERSIZE+1]; // Where the received command will be temporarily held. Add 1 for NULL terminator at the end.
String outputDataBuffer = ""; // We'll store a message here before sending it.

// Data chunk delimiters - used to split commands and values that follow them.
const char INPUT_START_CHAR = '>'; // At the start of every command message sent TO the Arduino.
const char OUTPUT_START_CHAR = '<'; // At the start of every command message sent FROM the Arduino.
const char END_CHAR = ';'; // End of the command message sent to and from the Arduino.
const char DATA_DELIMITER[2] = ","; // Splits the command name and value. For some reason has to be size 2.

Module* actuators[] = {&armModulesModule, &armActuatorModule, &engine1, &engine2, &engine3, &engine4, &sendSensorReadingsModule, &refreshRate, &forwardLED};
Module* sensors[] = {&depthSensor, &depthSensor2};

/* =============================================================================
 * MAIN FUNCTIONS DEFINITIONS.
 * =============================================================================
 */
void setup(void)
/* Prepare to listen to commands over serial and start everything up. */
{
	armModulesModule.setValue(0); // Don't arm the modules by default, wait for a command.
	armActuatorModule.setValue(-1); // Will arm the actuator that's under the index of armActuatorModule value.
	refreshRate.setValue(10); // Set default delay in milliseconds in the main loop
	forwardLED.setValue(0); // LEDs are off by default.
	
	// set modes for pins used by simple switch modules
	pinMode(ON_LED_PIN, OUTPUT);

	//TODO: do some system checks, like battery level, connections etc.

	// Start serial comms at the same baud rate as the engines.
	Serial.begin(engine1.serialBaudRate);
	
	Serial.println("ROV "+ROV_MODEL+" v. "+ROV_SW_VERSION+" listening to commands.");
}

void loop(void)
{
	// Light the LED to show the ROV is working and executing the main loop.
	digitalWrite(ON_LED_PIN, HIGH);

	// Get and set control inputs.
	if ( Serial.available())
	{
		if (getSerial()) // If we got a command over serial read it into the inputDataBuffer char array.
		{
			parseInput(); // Parse the telecommand and set appropriate actuator values.
		}
	}

	// Arm the modules if requested.
	if(armModulesModule.getValue()==1)
	{
		armModules(); // This function handles everything.
		armModulesModule.setValue(0); // We're done arming now.
	}
	
	// Arm the engine that was requested.
	if(armActuatorModule.getValue()!=-1)
	{
		// Arm whatever module the user wants.
		armActuator(armActuatorModule.getValue());
		armActuatorModule.setValue(-1); // Go back to default value.
	}
	
	// Send readings from all the sensors over serial after this has been requested by a command.
	if(sendSensorReadingsModule.getValue()==1)
	{
		sendSensorReadings(); // Send the readings.
		sendSensorReadingsModule.setValue(0); // Re-set the flag and wait for it to be send next time readings are required.
	}
	
	// Reduce rate at which stuff happens.
	delay(refreshRate.getValue());
}

/* =============================================================================
 * HELPER FUNCTIONS DEFINITIONS.
 * =============================================================================
 */

boolean getSerial(void)
/* Read input from the serial port and store it in the inputDataBuffer buffer.
 * The serial input has to conform to a protocol, whereby the messages begin with
 * INPUT_START_CHAR and terminate with END_CHAR. The message in between is
 * a sequence of strings and integers. Strings represent the destination of the 
 * command (e.g. engine throttle) and integers are the arguments for the command
 * (e.g. throttle value).
 *
 * @return - true if we've parsed the entire command successfully; false otherwise,
 * 			e.g. when we didn't receive a command.
 */
{
	static boolean placeInBuffer = false; // Only write data when working on a recognisable data chunk
	static byte dataBufferIndex = 0;
	char incomingbyte; // The currently read serial input byte.
	
	while(Serial.available()>0)
	{
		incomingbyte = Serial.read(); // Read bytes from the serial input one by one.

		if(incomingbyte==INPUT_START_CHAR) // A command has been received.
		{
			dataBufferIndex = 0; // We'll be reading the first input value next.
			placeInBuffer = true; // We should be storing the inputs in the buffer now.
		}

		if(placeInBuffer)
		{
			if(dataBufferIndex==DATABUFFERSIZE)
			{
				// Index is pointing to an array element outside our buffer.
				dataBufferIndex = 0; // We're done reading this command, so have to start reading the next one from the beginning.
				break; // Exit the while loop, we're done with this command.
			}
		
			if(incomingbyte==END_CHAR) // We've reached the end of this command.
			{
				inputDataBuffer[dataBufferIndex] = 0; // Null terminate the C string
				placeInBuffer = false; // Don't store anything here any more.
				dataBufferIndex = 0; // Make sure next command gets written to the start of the buffer.
				return true; // Say that we've parsed the whole command.
			}
			else if (incomingbyte!=INPUT_START_CHAR) // Simply record the telecommand byte.
			{
				inputDataBuffer[dataBufferIndex++] = incomingbyte;
			}
		}
	}

	return false; // Something went wrong or we didn't receive an actual command.
}

void parseInput(void)
/* Extract commands and corresponding numbers from the inputDataBuffer input buffer. */
{
  // Get the first data token.
  char * token;
  token = strtok(inputDataBuffer, DATA_DELIMITER);
  
  // Parse the entire inputDataBuffer of tokens (commands and their value arguments).
  int nextActuatorIndex = -1; // Index of the actuator value for which is sent in this part of the telecommand.
  
  while (token != NULL)
  {
  	// If next actuator index < 0 we have no value to read now
  	if (nextActuatorIndex >= 0)
  	{
  		#ifdef DEBUG_PRINTOUT
	  		Serial.print("ROV "+ROV_MODEL+" v. "+ROV_SW_VERSION+" trying to set value of actuator ");
	  		Serial.print(actuators[nextActuatorIndex]->getIdentifier());
	  		Serial.print(" to ");
	  		Serial.println( String(int(atof(token))) );
  		#endif
  		
  		actuators[nextActuatorIndex] -> setValue( int(atof(token)) );
  		// Indicate that on the next pass there is no value to read.
  		nextActuatorIndex = -1;
	}
	else
	{	
	  // Check what value is coming next strings
	  for(long int actuatorI=0;actuatorI<sizeof(actuators)/sizeof(actuators[0]);actuatorI++)
	  {
	  	if (strcmp(token, actuators[actuatorI]->getIdentifier()) == 0)
	  	{
	  		nextActuatorIndex = actuatorI;
	  		break;
	  	}
	  }
	}
        
	// Continue to the new token.
	token = strtok(NULL, DATA_DELIMITER);
  }
}

void sendSensorReadings(void)
/* Send a message over the USB bus according to the agreed telecommunications
 * protocol, containing a series of identifier strings followed by values of the
 * current sensors.
 */
{
	outputDataBuffer += OUTPUT_START_CHAR; // Start the message.
	for(long int i=0;i<sizeof(sensors)/sizeof(sensors[0]);i++)
	{
		outputDataBuffer += String( sensors[i]->getIdentifier() );
		outputDataBuffer += DATA_DELIMITER;
		outputDataBuffer += String( sensors[i]->getValue() );
		if(i<sizeof(sensors)/sizeof(sensors[0])-1) // Don't add a delimiter after the last sensor.
		{
			outputDataBuffer += DATA_DELIMITER;
		}
	}
	outputDataBuffer += END_CHAR; // Terminate the message.
	
	Serial.println( outputDataBuffer ); // Send the formatted message.
	outputDataBuffer = ""; // Restart the buffer so it's clean before sending the next message.
}

void armActuator(int idx)
/* Arm the actuator that's under the input index in the actuators array.
 * int idx - index of the actuators corresponding to the engine that will be armed.
 */
{
	int setupDelay = actuators[idx]->arm(); // Arm only this actuator.
		
	// Send the message saying how long the delay will last.
	outputDataBuffer += OUTPUT_START_CHAR; // Start the message.
	outputDataBuffer += "setupDelay";
	outputDataBuffer += DATA_DELIMITER;
	outputDataBuffer += String(setupDelay);
	outputDataBuffer += END_CHAR; // Terminate the message.
	Serial.println( outputDataBuffer ); // Send the formatted message.
	outputDataBuffer = ""; // Restart the buffer so it's clean before sending the next message.
	
	delay(setupDelay); // Wait for as long as required by the slowest arming module.
}

void armModules(void)
/* Arm all the modules registered in actuators and sensors arrays by calling their
 * arm methods and waiting for the requested duration. Wait for the longest
 * duration necessary to arm any module and send a message over serial saying for
 * how long Arduino  will be sleeping so that the GUI knows.
 */
{
	int setupDelay(0); // By default wait for 0 seconds, i.e. arm nothing.
	for(long int i=0;i<sizeof(actuators)/sizeof(actuators[0]);i++) // Arm all actuators.
	{
		int delayRequested = actuators[i]->arm();
		if (delayRequested > setupDelay) setupDelay = delayRequested;
	}
	for(long int i=0;i<sizeof(sensors)/sizeof(sensors[0]);i++) // Arm all sensors.
	{
		int delayRequested = sensors[i]->arm();
		if (delayRequested > setupDelay) setupDelay = delayRequested;
	}
	
	// Send the message saying how long the delay will last.
	outputDataBuffer += OUTPUT_START_CHAR; // Start the message.
	outputDataBuffer += "setupDelay";
	outputDataBuffer += DATA_DELIMITER;
	outputDataBuffer += String(setupDelay);
	outputDataBuffer += END_CHAR; // Terminate the message.
	Serial.println( outputDataBuffer ); // Send the formatted message.
	outputDataBuffer = ""; // Restart the buffer so it's clean before sending the next message.
	
	delay(setupDelay); // Wait for as long as required by the slowest arming module.
}
