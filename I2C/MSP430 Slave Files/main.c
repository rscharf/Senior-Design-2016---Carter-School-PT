/*** USCI slave library ********************************************************

In this file the usage of the USCI I2C slave code is shown. 
This code uses callback functions as an interface for the user. For each 
byte that is received or is to be transmitted the corresponding callback 
function is called by the USCI I2C function set.


Uli Kretzschmar
MSP430 Systems
Freising
*******************************************************************************/
#include "msp430.h"

#include "TI_USCI_I2C_slave.h"

void receive_cb(unsigned char receive);
void transmit_cb(unsigned char volatile *receive);
void set_address(unsigned char new_address);
void start_cb();

unsigned char set_add_flag = 0;
unsigned char TXData = 0 ;
unsigned char RXData = 0 ;
unsigned int byte_num = 0;
unsigned int state = 0;
unsigned char incomingData = 0;
unsigned char sensor_flag = 0;
unsigned int button_flag = 0;
//#define RESET_BUTT 8

// ADC variables
// Global variables that store the results (read from the debugger)
 volatile int latest_result;   // most recent result is stored in latest_result
 //volatile unsigned long conversion_count=0; //total number of conversions done
 volatile int adc_vals_before_ave = 0;
 volatile int adc_average = 0;
 volatile int adc_average_add = 0;
 volatile int adc_vals_array[5];
 volatile unsigned char last_button;
 volatile unsigned char last_button2;
 int blink_interval = 0;
 int blink_counter = 0;



// Declare variables in the information memory
#pragma DATA_SECTION(assigned_address,".infoD");
volatile const char assigned_address = 0x7f;

void main(void)
{
  //WDTCTL = WDTPW + WDTHOLD;                            // Stop WDT
  TI_USCI_I2C_slaveinit(start_cb, transmit_cb, receive_cb, assigned_address); // init the slave
  _EINT();
  BCSCTL1 = CALBC1_16MHZ; 
  DCOCTL = CALDCO_16MHZ; //16 MHz calibration for clock
  init_adc();
  init_wdt();
  	P1DIR |= RED;                             // Set RED to output direction
    P1OUT |= RED;							  // RED ON
    P1DIR |= BJT_OUT;
    P1DIR &= ~BUTTON;
    P1OUT &= ~BJT_OUT;
  //  P1OUT &= RED;
    P1OUT |= BUTTON;
    P1REN |= BUTTON;


    //writeDword(0x7f, (char *) &assigned_address); //reset address to broadcast address in flash mem
  //LPM0;                                                // Enter LPM0.
  _bis_SR_register(GIE+LPM0_bits);
}

void start_cb(){
  RXData = 0;
}

// Receive callback function. Values received are interpreted based on current state
// RPi should pass first the state and then the data and MSP will act accordingly
void receive_cb(unsigned char receive){
  byte_num++; //increases by 2 for every time this function is called
  if (byte_num == 2){ //first byte passed = state
	  state = receive;
  }
  else if (byte_num == 4){ //second byte passed is data (data is now stored in variable receive)
	  byte_num = 0;
  }

 // if (receive == 0x01) //Just for debugging purposes
	//  P1OUT ^= RED; //Turn RED off if a certain value is received

  if (byte_num == 0) //if data has just been received
  {
   switch(state) // Save new address to flash memory
   {
   	   case 0: //idle state
   		   break;
   	   case 1: // setting new address
   		   eraseD(); //Erase Data in D
   		   writeDword(receive, (char *) &assigned_address);//SET NEW ADDRESS in flash mem
   		   UCB0I2COA = assigned_address; // Set slave address register to address stored in flash mem

   		   break;
   	   case 2: //panel active and listening for sensor trigger
   		   break; //data received doesn't matter
   	   case 3: //panel has been triggered, lights on
   		   break;
   	   case 4:
   		   break; //data received doesn't matter
   	   default:
   		   break;
   }

    }

}

void transmit_cb(unsigned char volatile *byte){
	 switch(state) // Save new address to flash memory
	   {
	   	   case 0: //idle state
	   		   *byte = 0;
	   		   break;
	   	   case 1: // setting new address
	   		   *byte = assigned_address; //Send slave's address to master (retreived from flash mem)
	   		   state = 0; //reset to Idle state
	   		   break;
	   	   case 2: //panel active and listening for sensor trigger
	   		   *byte = sensor_flag; //Pass 0 if flag hasn't been triggered. pass 1 if flag has been triggered
	   		   break; //data received doesn't matter
	   	   case 3:
	   		   *byte = 1;
	   		   break; //idle state with lights on, no action in transmit/receive necessary
	   	   case 4:
	   		   if ((sensor_flag == 1) || (button_flag == 1)){
	   			*byte = 1;
	   			sensor_flag = 0;
	   			button_flag = 0;
	   			state = 3;
	   		   }
	   		   else *byte = 0;
	   		   //
	   		   //}
	   		   //else *byte = 0; //Pass 0 if button hasn't been pressed, pass 1 if it has been pressed
	   	   default:
	   		   *byte = 0;
	   		   break;
	   }
}

/*
 * The ADC handler is invoked when a conversion is complete.
 * Its action here is to simply store the result in memory.
 */
 void interrupt adc_handler(){
	 latest_result=ADC10MEM;   // store the answer
 }
 ISR_VECTOR(adc_handler, ".int05")


// ===== Watchdog Timer Interrupt Handler =====
interrupt void WDT_interval_handler(){

	 	 if (state == 4) {
						ADC10CTL0 |= ADC10SC;  // trigger a conversion

						//button handling - for now this button acts as a sensor+
						unsigned char b;
						b= (P1IN & BUTTON);  // read the BUTTON bit
						if (last_button && (b==0))
						{ // has the button bit gone from high to low
						  //turn off LEDs and reset COM_OUT to low
							P1OUT ^= RED;
							//P1OUT &= ~BJT_OUT;
							button_flag = 1;
						}
						last_button=b;    // remember button reading for next time.


						int j;
						for (j=0; j<5; j++)
						{
							adc_average_add = adc_average_add + adc_vals_array[j];
						}
						adc_average = adc_average_add/5;
						adc_average_add = 0;

						if ((adc_average > IR_THRESHOLD))
						{
							//P1OUT |= RED;
							P1OUT |= BJT_OUT;
							P1OUT &= ~RED;

							sensor_flag = 1;
						}

						if (adc_vals_before_ave == 5)
						{
							adc_vals_before_ave = 0;
						}
						else
						{
							adc_vals_array[adc_vals_before_ave] = latest_result;
							adc_vals_before_ave++;
						}

	 	 }

}

ISR_VECTOR(WDT_interval_handler, ".int10")
