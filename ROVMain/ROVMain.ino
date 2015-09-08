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
 * @since:  6 Sep 2015
 * @version: 2.0.0
 * 
 * CHANGELOG
 *  5 Sep 2015 - 1.0.0 - Alek Lidtke - released the first version.
 *  6 Sep 2015 - 2.0.0 - Alek & Artur Lidtke - derived motor class from the Module class.
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
// Labels that will be used to identify the thrust and action commands for individual engines and actuators.
const char* ENGINE_LABEL_1 = "motorPortHor"; // Port engine giving horizontal thrust.
const char* ENGINE_LABEL_2 = "motorStbdHor"; // Starboard engine giving horizontal thrust.
const char* ENGINE_LABEL_3 = "motorPortVer"; // Port engine giving vertical thrust.
const char* ENGINE_LABEL_4 = "motorStbdVer"; // Starboard engine giving vertical thrust.

// Motor instances.
BrushlessDCMotor engine1, engine2, engine3, engine4; // Interfaces to the brushless motors.

// Motor pin assignments.
const int MOTOR_1_PIN = 9; // Pin to which the first motor is connected.
const int RELAY_1_PIN = 8; // Relay that reverses the direction of this motor is attached to this pin.

/* =============================================================================
 * MISC ACTUATOR DEFINITIONS.
 * =============================================================================
 */
const char* LED_LABEL = "forwardLED"; // Whether forward illumination LED is on or of.
const int FORWARD_LED_PIN = 12; // When this is set HIGH the forward light will switch on.

const int ON_LED_PIN = 13; // LED on the Arduino board that will be lit when the ROV is in the main loop.

/* =============================================================================
 * SENSOR DEFINITIONS.
 * =============================================================================
 */
// Commands that will be sent to the Arduino to request data from sensors.
const char* DEPTH_SENSOR_LABEL = "depthReading"; // Used to request data from the depth sensor.

DepthSensor depthSensor;

/* =============================================================================
 * TELECOMMAND PROTOCOL DEFINITION.
 * =============================================================================
 */
const int REFRESH_RATE = 100; // How many milliseconds to wait before checking for input commands.

// Input and output data buffers.
#define DATABUFFERSIZE 80
char inputDataBuffer[DATABUFFERSIZE+1]; // Where the received command will be temporarily held. Add 1 for NULL terminator at the end.
String outputDataBuffer = ""; // We'll store a message here before sending it.

// Data chunk delimiters - used to split commands and values that follow them.
const char INPUT_START_CHAR = '>'; // At the start of every command message sent TO the Arduino.
const char OUTPUT_START_CHAR = '<'; // At the start of every command message sent FROM the Arduino.
const char END_CHAR = ';'; // End of the command message sent to and from the Arduino.
const char DATA_DELIMITER[2] = ","; // Splits the command name and value. For some reason has to be size 2.

Module* actuators[] = {&engine1, &engine2, &engine3, &engine4};
Module* sensors[] = {&depthSensor};

/* =============================================================================
 * FUNCTIONS DEFINITIONS.
 * =============================================================================
 */
void setup(void)
/* Prepare to listen to commands over serial and start everything up. */
{
//TODO: do some system checks, like battery level, connections etc.

//TODO: add more motors.
	engine1 = BrushlessDCMotor(ENGINE_LABEL_1, 100, 2200, 800, MOTOR_1_PIN, RELAY_1_PIN); // These pule widths correspond to the currently selected electronic speed controller (ESC) - Turningy EA-
	Serial.begin(engine1.serialBaudRate); // Start serial comms at the same baud rate as the engines.
		
	engine1.setPulseWidth(1100); // Arm the motor by setting the control at zero throttle position.
	delay(25000);
	Serial.println("Armed the motors.");

//TODO: initialise all the sensors etc.
	depthSensor = DepthSensor("depthReading",15);
	
	Serial.println("ROV listening to commands."); //TODO: could add VERSION, ROVMODEL etc. consts somewhere so we know what ROV we're using.
}

void loop(void)
{    
	// Light the LED to show the ROV is working and executing the main loop.
	digitalWrite(ON_LED_PIN, HIGH);

	// Get control inputs.
	if ( Serial.available())
		{
		if (getSerial()) // If we got a command over serial read it into the inputDataBuffer char array.
		{
		  parseInput(); // Parse the telecommand.
		}
	}

	// Periodically send readings from all the sensors over serial.
	sendSensorReadings();
	
	// Reduce rate at which stuff happens.
	delay(REFRESH_RATE);
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
	outputDataBuffer[0] = OUTPUT_START_CHAR; // Start the message.
	for(int i=0;i<sizeof(sensors)/sizeof(sensors[0]);i++)
	{
		outputDataBuffer += String( sensors[i]->getValue() );
		outputDataBuffer += DATA_DELIMITER;
	}
	outputDataBuffer += END_CHAR; // Terminate the message.
	
	Serial.println( outputDataBuffer ); // Send the formatted message.
	outputDataBuffer = ""; // Restart the buffer so it's clean before sending the next message.
}
