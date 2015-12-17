#include <msp430g2553.h>
#include "TI_USCI_I2C_master.h"

/*
 * master.c
 */


//Bit positions in P1 for SPI
#define BUTTON  0x08 //P1.3 = on board button
#define GREEN 0x40
#define SDA 0x02 //P1.1 = SDA
#define CLK 0x04 //p1.2 = CLK
void init_i2c(void);
void init_wdt(void);


unsigned char array[5] = { 0x1, 0x2, 0x3, 0x4, 0x5 };

unsigned int data_received = 0; //most recent byte received
volatile unsigned char last_button;
void init_wdt(){
	// setup the watchdog timer as an interval timer
  	WDTCTL =(WDTPW +		// (bits 15-8) password
     	                   	// bit 7=0 => watchdog timer on
       	                 	// bit 6=0 => NMI on rising edge (not used here)
                        	// bit 5=0 => RST/NMI pin does a reset (not used here)
           	 WDTTMSEL +     // (bit 4) select interval timer mode
  		     WDTCNTCL  		// (bit 3) clear watchdog timer counter
  		                	// bit 2=0 => SMCLK is the source
  		                	// bits 1-0 = 10=> source/512
 			 );
  	IE1 |= WDTIE; // enable WDT interrupt
 }


interrupt void WDT_interval_handler(){

	unsigned char b;
	  	b= (P1IN & BUTTON);  // read the BUTTON bit
	  	if (last_button && (b==0)){ // has the button bit gone from high to low
	  		P1OUT ^= GREEN; // toggle both LED's
	  	}
	  	last_button=b;    // remember button reading for next time.

}
// DECLARE function WDT_interval_handler as handler for interrupt 10
// using a macro defined in the msp430g2553.h include file
ISR_VECTOR(WDT_interval_handler, ".int10")

void init_i2c(){
		UCB0CTL1 |= UCSWRST;				//Enable SW reset
		UCB0CTL1 = UCSSEL_2+UCSWRST;  		// Reset state machine; SMCLK source;
		UCB0CTL0 = UCCKPH + UCMST + UCMODE_3 + UCSYNC;// I2C Master, synchronous mode (needed for SPI or I2C)
		UCB0CTL1 = UCSSEL_2 + UCSWRST;            // Use SMCLK, keep SW reset
		UCB0BR0 = 12;                             // fSCL = SMCLK/12 = ~100kHz
		UCB0BR1 = 0;
		UCB0I2CSA = 0x4e;                         // Set slave address

		UCB0CTL1 &= ~UCSWRST;				// Clear SW reset, resume operation
		IFG2 &= ~UCB0RXIFG;					// clear UCB0 RX flag
		IE2 |= UCB0RXIE;					// enable UCB0 RX interrupt
		IE2 |= UCB0TXIE;                    // Enable TX interrupt


		 P1SEL |= BIT6 + BIT7;                     // Assign I2C pins to USCI_B0
		 P1SEL2|= BIT6 + BIT7;                     // Assign I2C pins to USCI_B0
}

//interrupt handler for received data
// The USCIAB0TX_ISR is structured such that it can be used to receive any
// 2+ number of bytes by pre-loading RxByteCtr with the byte count.


void main(void) {
    WDTCTL = WDTPW | WDTHOLD;	// Stop watchdog timer


	//init_i2c();
	//init_wdt();
	//P1DIR |= GREEN; //Set red button to output
	//P1OUT &~ GREEN; // Green on
	//P1DIR &= ~BUTTON;	//set button to input
	//P1OUT |= BUTTON;
	//P1REN |= BUTTON;	// Activate pullup resistors on Button Pin
	
    _EINT(); //enable interrupts
    TI_USCI_I2C_transmitinit(0x48, 0x3f); //initialize USCI
    while (TI_USCI_I2C_notready() ); //wait for bus to be free
    TI_USCI_I2C_transmit(3, array); //transmit first three bytes of array
	_bis_SR_register(GIE+LPM0_bits); //enable interrupts
}
