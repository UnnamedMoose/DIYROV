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
 * @since: 24 Sep 2015
 * @version: 2.1.0
 * 
 * CHANGELOG
 *  5 Sep 2015 - 1.0.0 - Alek Lidtke - released the first version.
 *  6 Sep 2015 - 2.0.0 - Alek & Artur Lidtke - derived motor class from the Module class.
 * 24 Sep 2015 - 2.1.0 - Alek Lidtke - added command handling via dummy Modules.
 */

// Custom includes.
#include "Module.h"
#include "BrushlessDCMotor.h"
#include "DepthSensor.h"
#include "Servo.h"

// Standard c/C++ includes
#include <stdio.h>

/* =============================================================================
 * FUNCTION DECLARATIONS.
 * =============================================================================
 */
void parseInput(void);
boolean getSerial(void);
void sendSensorReadings(void);

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
	MOTOR_MIN_PULSE_WIDTH, MOTOR_ARM_PULSE_WIDTH, 9, 8);
BrushlessDCMotor engine2 = BrushlessDCMotor("motorStbdHor", THROTTLE_STEPS, MOTOR_MAX_PULSE_WIDTH,
	MOTOR_MIN_PULSE_WIDTH, MOTOR_ARM_PULSE_WIDTH, 6, 7);
BrushlessDCMotor engine3 = BrushlessDCMotor("motorPortVer", THROTTLE_STEPS,MOTOR_MAX_PULSE_WIDTH,
	MOTOR_MIN_PULSE_WIDTH, MOTOR_ARM_PULSE_WIDTH, 5, 4);
BrushlessDCMotor engine4 = BrushlessDCMotor("motorStbdVer", THROTTLE_STEPS, MOTOR_MAX_PULSE_WIDTH,
	MOTOR_MIN_PULSE_WIDTH, MOTOR_ARM_PULSE_WIDTH, 3, 2);

/* =============================================================================
 * MISC ACTUATOR DEFINITIONS.
 * =============================================================================
 */
Module sendSensorReadingsModule = Module("sendSensorReadings"); // Sends sensor readings over serial.

Module refreshRate = Module("refreshRate"); // Changes the delay in the main loop.

Module forwardLED = Module("forwardLED"); // Switches the forward illumination LED on or of.
const int FORWARD_LED_PIN = 12; // When this is set HIGH the forward light will switch on.

const int ON_LED_PIN = 13; // LED on the Arduino board that will be lit when the ROV is in the main loop.

/* =============================================================================
 * SENSOR DEFINITIONS.
 * =============================================================================
 */
DepthSensor depthSensor = DepthSensor("depthReading",15); // For now a mock sensor.
DepthSensor depthSensor2 = DepthSensor("depthReading2",16); // Another mock sensor to make sure the message concatenation works well.

/* =============================================================================
 * TELECOMMAND PROTOCOL DEFINITION.
 * =============================================================================
 */
// Input and output data buffers.
#define DATABUFFERSIZE 80
char inputDataBuffer[DATABUFFERSIZE+1]; // Where the received command will be temporarily held. Add 1 for NULL terminator at the end.
String outputDataBuffer = ""; // We'll store a message here before sending it.

// Data chunk delimiters - used to split commands and values that follow them.
const char INPUT_START_CHAR = '>'; // At the start of every command message sent TO the Arduino.
const char OUTPUT_START_CHAR = '<'; // At the start of every command message sent FROM the Arduino.
const char END_CHAR = ';'; // End of the command message sent to and from the Arduino.
const char DATA_DELIMITER[2] = ","; // Splits the command name and value. For some reason has to be size 2.

Module* actuators[] = {&engine1, &engine2, &engine3, &engine4, &sendSensorReadingsModule, &refreshRate, &forwardLED};
Module* sensors[] = {&depthSensor, &depthSensor2};

/* =============================================================================
 * FUNCTIONS DEFINITIONS.
 * =============================================================================
 */
void setup(void)
/* Prepare to listen to commands over serial and start everything up. */
{
	refreshRate.setValue(100); // Set default delay in milliseconds in the main loop/

	//TODO: do some system checks, like battery level, connections etc.

	// Start serial comms at the same baud rate as the engines.
	Serial.begin(engine1.serialBaudRate);
	
	// Arm all the modules.
	int setupDelay(0);
	for(int i=0;i<sizeof(actuators)/sizeof(actuators[0]);i++)
	{
		int delayRequested = actuators[i]->arm();
		if (delayRequested > setupDelay) setupDelay = delayRequested;
	}
	for(int i=0;i<sizeof(sensors)/sizeof(sensors[0]);i++)
	{
		int delayRequested = sensors[i]->arm();
		if (delayRequested > setupDelay) setupDelay = delayRequested;
	}
	delay(setupDelay); // Wait for as long as required by the slowest arming module.
	
	//TODO: do whatever else operations we want to do at start-up.
	
	Serial.println("ROV listening to commands."); //TODO: could add VERSION, ROVMODEL etc. consts somewhere so we know what ROV we're using.
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

	// Send readings from all the sensors over serial after this has been requested by a command.
	if(sendSensorReadingsModule.getValue()==1)
	{
		sendSensorReadings();
	}
	
	// Reduce rate at which stuff happens.
	delay(refreshRate.getValue());
}

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
  token = strtok (inputDataBuffer, DATA_DELIMITER);
  
  // Parse the entire inputDataBuffer of tokens (commands and their value arguments).
  int nextActuatorIndex = -1; // Index of the actuator value for which is sent in this part of the telecommand.
  
  while (token != NULL)
  {
  
  	// If next actuator index < 0 we have no value to read now
  	if (nextActuatorIndex >= 0)
  	{
  		Serial.print("ROV trying to set value of actuator ");
  		Serial.print(actuators[nextActuatorIndex]->getIdentifier());
  		Serial.print(" to ");
  		Serial.println( String(int(atof(token))) );
  		actuators[nextActuatorIndex] -> setValue( int(atof(token)) );
  		// Indicate that on the next pass there is no value to read.
  		nextActuatorIndex = -1;
	}
	else
	{	
	  // Check what value is coming next strings
	  for(int actuatorI=0;actuatorI<sizeof(actuators)/sizeof(actuators[0]);actuatorI++)
	  {
	  	if (strcmp(token, actuators[actuatorI]->getIdentifier()) == 0)
	  	{
	  		nextActuatorIndex = actuatorI;
	  		break;
	  	}
	  }
	}
        
	// Continue to the new token.
	token = strtok (NULL, DATA_DELIMITER);
  }
}

void sendSensorReadings(void)
/* Send a message over the USB bus according to the agreed telecommunications
 * protocol, containing a series of identifier strings followed by values of the
 * current sensors.
 */
{
	outputDataBuffer += OUTPUT_START_CHAR; // Start the message.
	for(int i=0;i<sizeof(sensors)/sizeof(sensors[0]);i++)
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
