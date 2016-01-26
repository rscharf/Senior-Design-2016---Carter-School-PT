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
void start_cb();
unsigned char flag=0;
unsigned char flag1=0;
unsigned char TXData = 0 ;
unsigned char RXData = 0 ;

void main(void)
{
  WDTCTL = WDTPW + WDTHOLD;                            // Stop WDT
  
  TI_USCI_I2C_slaveinit(start_cb, transmit_cb, receive_cb, 0x07);// init the slave
  _EINT();
  BCSCTL1 = CALBC1_16MHZ; 
  DCOCTL = CALDCO_16MHZ;
  LPM0;                                                // Enter LPM0.
}

void start_cb(){
  RXData = 0;
}

void receive_cb(unsigned char receive){
  RXData = receive;
    flag1++;
}

void transmit_cb(unsigned char volatile *byte){
  *byte = TXData++;
  flag++;
}


