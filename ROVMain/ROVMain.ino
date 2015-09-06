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
 * @since:  5 Sep 2015
 * @version: 1.0.0
 * 
 * CHANGELOG
 *  5 Sep 2015 - 1.0.0 - Alek Lidtke - released the first version.
 */

// Custom includes.
#include "BrushlessDCMotor.h"
#include "Servo.h"

// Standard c/C++ includes
#include <stdio.h>

// Function declarations.
void parseInput(void);
boolean getSerial(void);

// Input data buffer
#define DATABUFFERSIZE 80
char dataBuffer[DATABUFFERSIZE+1]; // Where the command will be temporarily held. Add 1 for NULL terminator at the end.

// Data chunk delimiters - used to split commands and values that follow them.
const char INPUT_START_CHAR = '>'; // At the start of every command message.
const char INPUT_END_CHAR = ';'; // End of the command message.
const char DATA_DELIMITER[2] = ","; // Splits the command name and value.

// ROV hardware pins and settings.
const int ON_LED_PIN = 13; // LED on the Arduino board that will be light when the ROV is in the main loop.
const int REFRESH_RATE = 100; // How many milliseconds to wait before checking for input commands.

// Labels that will be used to identify the thrust commands for individual engines.
const char* ENGINE_LABEL_1 = "motorPortHor"; // Port engine giving horizontal thrust.
const char* ENGINE_LABEL_2 = "motorStbdHor"; // Starboard engine giving horizontal thrust.
const char* ENGINE_LABEL_3 = "motorPortVer"; // Port engine giving vertical thrust.
const char* ENGINE_LABEL_4 = "motorStbdVer"; // Starboard engine giving vertical thrust.

BrushlessDCMotor engine1, engine2, engine3, engine4; // Interfaces to the brushless motors.

const int MOTOR_1_PIN = 9; // Pin to which the first motor is connected.
const int RELAY_1_PIN = 8; // Relay that reverses the direction of this motor is attached to this pin.

void setup(void)
/* Prepare to listen to commands over serial and start everything up. */
{
//TODO: do some system checks, like battery level, connections etc.

//TODO: add more motors.
	engine1 = BrushlessDCMotor(1, 100, 2200, 800, MOTOR_1_PIN, RELAY_1_PIN); // These pule widths correspond to the currently selected electronic speed controller (ESC) - Turningy EA-25A. 
	engine1.setPulseWidth(1100); // Arm the motor by setting the control at zero throttle position.
	delay(25000);
	Serial.println("Armed the motors.");

//TODO: initialise all the sensors etc.
	Serial.begin(engine1.serialBaudRate); // Start serial comms at the same baud rate as the engine.
	Serial.println("ROV listening to commands."); //TODO: could add VERSION, ROVMODEL etc. consts somewhere so we know what ROV we're using.
}

void loop(void)
{    
	// Light the LED to show the ROV is working and executing the main loop.
	digitalWrite(ON_LED_PIN, HIGH);

	// Get control inputs.
	if ( Serial.available())
		{
		if (getSerial()) // If we got a command over serial read it into the dataBuffer char array.
		{
		  parseInput(); // Parse the telecommand.
		}
	}

	// Reduce rate at which stuff happens.
	delay(REFRESH_RATE);
}

boolean getSerial()
/* Read input from the serial port and store it in the dataBuffer buffer.
 * The serial input has to conform to a protocol, whereby the messages begin with
 * INPUT_START_CHAR and terminate with INPUT_END_CHAR. The message in between is
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
		
			if(incomingbyte==INPUT_END_CHAR) // We've reached the end of this command.
			{
				dataBuffer[dataBufferIndex] = 0; // Null terminate the C string
				placeInBuffer = false; // Don't store anything here any more.
				dataBufferIndex = 0; // Make sure next command gets written to the start of the buffer.
				return true; // Say that we've parsed the whole command.
			}
			else if (incomingbyte!=INPUT_START_CHAR) // Simply record the telecommand byte.
			{
				dataBuffer[dataBufferIndex++] = incomingbyte;
			}
		}
	}

	return false; // Something went wrong or we didn't receive an actual command.
}

void parseInput()
/* Extract numbers from the dataBuffer input buffer. */
{
  // Variables that indicate which numbers are coming next.
  boolean engine1Next, engine2Next, engine3Next, engine4Next = false;
  
  int currentValue = 0; // Temporary variable that holds the value for the current part of the command.
  
  // Get the first data token.
  char * token;
  token = strtok (dataBuffer, DATA_DELIMITER);
  
  // Parse the entire dataBuffer of tokens (commands and their value arguments).
  while (token != NULL)
  {
      // Check what value is coming next strings
      if (strcmp(token, ENGINE_LABEL_1) == 0)
      {
        engine1Next = true;
      }
      else if (strcmp(token, ENGINE_LABEL_2) == 0)
      {
        engine2Next = true;
      }
      else if (strcmp(token, ENGINE_LABEL_3) == 0)
      {
        engine3Next = true;
      }
      else if (strcmp(token, ENGINE_LABEL_4) == 0)
      {
        engine4Next = true;
      }
      
      // Check if any of the available numbers are in the token right now.
      else if (engine1Next)
      {
        currentValue = atof(token);
        Serial.print("ROV trying toset thrust to ");Serial.println( String(currentValue) );
        engine1.setThrust(currentValue); // Scale the desired throttle to pulse width and actually make the engine spin at the desired RPM.
        engine1Next = false;
      }
      else if (engine2Next)
      {
        currentValue = atof(token);
        engine2Next = false;
      }
      else if (engine3Next)
      {
        currentValue = atof(token);
        engine3Next = false;
      }
      else if (engine4Next)
      {
        currentValue = atof(token);
        engine4Next = false;
      }
      
      // Get a new token.
      token = strtok (NULL, DATA_DELIMITER);
  }
}
