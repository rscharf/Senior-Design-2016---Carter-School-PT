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
unsigned char flag=0;
unsigned char flag1=0;
unsigned char set_add_flag = 0;
unsigned char TXData = 0 ;
unsigned char RXData = 0 ;
unsigned int byte_num = 0;
unsigned int state = 0;
unsigned char incomingData = 0;

// Declare variables in the information memory
#pragma DATA_SECTION(assigned_address,".infoD");
volatile const char assigned_address = 0x7f;

void main(void)
{
  WDTCTL = WDTPW + WDTHOLD;                            // Stop WDT
  TI_USCI_I2C_slaveinit(start_cb, transmit_cb, receive_cb, 0x7f); // init the slave
  _EINT();
  BCSCTL1 = CALBC1_16MHZ; 
  DCOCTL = CALDCO_16MHZ;
  LPM0;                                                // Enter LPM0.
}

void start_cb(){
  RXData = 0;
}

void receive_cb(unsigned char receive){
  byte_num++; //increases by 2 for every time this function is called
  if (byte_num == 2){ //first byte passed = state
	  state = receive;
  }
  else if (byte_num == 4){ //second byte passed is data
	  byte_num = 0;
  }

  if (receive == 0x01)
	  P1OUT ^= RED; //Turn RED off if a certain value is received


   if ((state == 1)&&(byte_num == 0)) // Save new address to flash memory
   {
    	 eraseD(); //Erase Data in D
    	 writeDword(receive, (char *) &assigned_address);//SET NEW ADDRESS in flash mem

    	 UCB0I2COA = assigned_address; // Set slave address register to address stored in flash mem
    	 state = 0; //reset to Idle state
    }



    flag1++;

}

void transmit_cb(unsigned char volatile *byte){

	*byte = assigned_address; //Send slave's address to master (retreived from flash mem)
	flag++;
}


