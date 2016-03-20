/*** USCI slave library ********************************************************

In this file the usage of the USCI I2C slave code is shown. 
This code uses callback functions as an interface for the user. For each 
byte that is received or is to be transmitted the corresponding callback 
function is called by the USCI I2C function set.


PWM HELP:
http://coder-tronics.com/msp430-timer-pwm-tutorial/

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
unsigned int new_duty_cycle = 0;
//#define RESET_BUTT 8
/*** Global Variable ***/
int IncDec_PWM = 1;
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

   TI_USCI_I2C_slaveinit(start_cb, transmit_cb, receive_cb, assigned_address); // init the slave
  _EINT();
  BCSCTL1 = CALBC1_16MHZ; 
  DCOCTL = CALDCO_16MHZ; //16 MHz calibration for clock
  init_adc();
  init_wdt();


  	P1DIR |= RED;                             // Set RED to output direction
    P1DIR |= BJT_OUT;
    P1DIR &= ~BUTTON;
    P1OUT &= ~BJT_OUT;

    P1OUT |= BUTTON;
    P1REN |= BUTTON;

    	/*** GPIO Set-Up ***/
        P1SEL |= BJT_OUT;					// BJT selected Timer0_A Out1 output

    	/*** Timer0_A Set-Up ***/
        TA0CCR0 |= 100;					// PWM period
        TA0CCR1 |= 0;					// TA0CCR1 PWM duty cycle
        TA0CCTL1 |= OUTMOD_7;			// TA0CCR1 output mode = reset/set
        TA0CTL |= TASSEL_2 + MC_1;		// SMCLK, Up Mode (Counts to TA0CCR0)


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

  if (byte_num == 0) //if data has just been received
  {
   switch(state) // Save new address to flash memory
   {
   	   case 0: //idle state
   		   P1OUT &= ~RED; //turn off on board LED?
   		   //P1OUT &= ~BJT_OUT; //turn off BJT LEDs
   		   TA0CCR1 = receive;
   		   break;
   	   case 1: // setting new address
   		   eraseD(); //Erase Data in D
   		   writeDword(receive, (char *) &assigned_address);//SET NEW ADDRESS in flash mem
   		   UCB0I2COA = assigned_address; // Set slave address register to address stored in flash mem
   		   break;
   	   case 2: //panel active and listening for sensor trigger
   		   break; //data received doesn't matter
   	   case 3: //idle state with lights activated - turn on LEDs
   		   //pi
   		   TA0CCR1 = receive; //set new duty cycle to value of brightness preference
   		   P1OUT |= BJT_OUT; //Turn on BJT LEDs
   		   P1OUT |= RED; //Turn on on-board LED
   		   sensor_flag = 0;
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
	   		   P1OUT &= ~BJT_OUT; //Turn off BJT LEDs
	   		   P1OUT &= ~RED; //Turn off on-board LED
	   		   break;
	   	   case 1: // setting new address
	   		   *byte = assigned_address; //Send slave's address to master (retreived from flash mem)
	   		   state = 0; //reset to Idle state after new address is sent to master
	   		   break;
	   	   case 2: //panel active and listening for sensor trigger
	   		   if ((sensor_flag == 1))
	   		   {
    			*byte = 1;
    			sensor_flag = 0;
    			button_flag = 0;
	   			//state = 3; //Dont enter state 3 until told by RPI..later
	   		   }
	   		   else *byte = 0;
	   		   break; //data received doesn't matter
	   	   case 3: //idle state with lights activated, no action in transmit necessary
	   		   *byte = 0;
	   		   break;
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

{
						ADC10CTL0 |= ADC10SC;  // trigger a conversion
						//Reset button. Should this only be accessible from state 2/3?
						//button handling - for now this button acts as a sensor+
						unsigned char b;
						b= (P1IN & BUTTON);  // read the BUTTON bit
						if (last_button && (b==0))
						{ // has the button bit gone from high to low
						  //turn off LEDs and go back to idle state
							//P1OUT ^= RED;
							P1OUT &= ~RED; //turn off on board LED?
							P1OUT &= ~BJT_OUT; //turn off BJT LEDs
							button_flag = 1;
							state = 0;
						}
						last_button=b;    // remember button reading for next time.


						int j;
						for (j=0; j<5; j++)
						{
							adc_average_add = adc_average_add + adc_vals_array[j];
						}
						adc_average = adc_average_add/5;
						adc_average_add = 0;

						if ((adc_average > IR_THRESHOLD) && (state == 2))
						{
							//P1OUT |= RED;
							sensor_flag = 1; //indicate sensor trigger
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
