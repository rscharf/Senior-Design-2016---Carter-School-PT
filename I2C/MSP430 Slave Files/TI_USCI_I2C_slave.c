//******************************************************************************
//   MSP430 USCI I2C Transmitter and Receiver (Slave Mode)
//
//  Description: This code configures the MSP430's USCI module as
//  I2C slave capable of transmitting and receiving bytes.
//
//  ***THIS IS THE SLAVE CODE***
//
//                    Slave
//                 MSP430F2619
//             -----------------
//         /|\|              XIN|-
//          | |                 |
//          --|RST          XOUT|-
//            |                 |
//            |                 |
//            |                 |
//            |         SCL/P1.6|------->
//            |         SDA/P1.7|------->
//
// Note: External pull-ups are needed for SDA & SCL
//
// Uli Kretzschmar
// Texas Instruments Deutschland GmbH
// November 2007
// Built with IAR Embedded Workbench Version: 3.42A
//
//******************************************************************************
// Modified by S. Wendler, Mai 2013 to work with MSP430G2553 and msp-gcc
//******************************************************************************

#include "TI_USCI_I2C_slave.h"

#include <msp430.h>


void (*TI_receive_callback)(unsigned char receive);
void (*TI_transmit_callback)(unsigned char volatile *send_next);
void (*TI_start_callback)(void);
unsigned char data_received = 0 ;


//------------------------------------------------------------------------------
// void TI_USCI_I2C_slaveinit(void (*SCallback)(),
//                            void (*TCallback)(unsigned char volatile *value),
//                            void (*RCallback)(unsigned char value),
//                            unsigned char slave_address)
//
// This function initializes the USCI module for I2C Slave operation.
//
// IN:   void (*SCallback)() => function is called when a START condition was detected
//       void (*TCallback)(unsigned char volatile *value) => function is called for every byte requested by master
//       void (*RCallback)(unsigned char value) => function is called for every byte that is received
//       unsigned char slave_address  =>  Slave Address
//------------------------------------------------------------------------------
void TI_USCI_I2C_slaveinit(void (*SCallback)(),
                           void (*TCallback)(unsigned char volatile *value),
                           void (*RCallback)(unsigned char value),
                           unsigned char slave_address)
{
    P1SEL |= SDA_PIN + SCL_PIN;               // Assign I2C pins to USCI_B0
    P1SEL2 |= SDA_PIN + SCL_PIN;              // Assign I2C pins to USCI_B0
    UCB0CTL1 |= UCSWRST;                      // Enable SW reset
    UCB0CTL0 = UCMODE_3 + UCSYNC;             // I2C Slave, synchronous mode
    UCB0I2COA = slave_address;                // set own (slave) address
    UCB0CTL1 &= ~UCSWRST;                     // Clear SW reset, resume operation
    IE2 |= UCB0TXIE + UCB0RXIE;               // Enable TX interrupt
    UCB0I2CIE |= UCSTTIE;                     // Enable STT interrupt
    TI_start_callback = SCallback;			  // Set callback functions
    TI_receive_callback = RCallback;
    TI_transmit_callback = TCallback;

}


// USCI_B0 Data ISR
#pragma vector = USCIAB0TX_VECTOR
__interrupt void USCIAB0TX_ISR(void)
{
  if (IFG2 & UCB0TXIFG){
    TI_transmit_callback(&UCB0TXBUF);

  }
  else
    TI_receive_callback(UCB0RXBUF);

}

// USCI_B0 State ISR
#pragma vector = USCIAB0RX_VECTOR
__interrupt void USCIAB0RX_ISR(void)
{
  UCB0STAT &= ~UCSTTIFG;                    // Clear start condition int flag
  TI_start_callback();
  IFG2 &= ~UCB0RXIFG;		 // clear UCB0 RX flag
}




void eraseD(){ // erase information memory segment D
	// assumes watchdog timer already disabled (which is necessary)
	FCTL2 = FWKEY+FSSEL_2+23; // SMCLK source + divisor 24 (assuming 8Mhz clock)
	FCTL3 = FWKEY; // unlock flash (except for segment A)
	FCTL1 = FWKEY+ERASE; // setup to erase
	*( (int *) 0x1000)  = 0; // dummy write to segment D word 0
	/* since this code is in flash, there is no need to explicitly wait
	 * for completion since the CPU is stopped while the flash controller
	 * is erasing or writing
	 */
	FCTL1=FWKEY; // clear erase and write modes
	FCTL3=FWKEY+LOCK; // relock the segment
}

void writeDword(char value, char *address){
	// write a single word.
	// NOTE: call only once for a given address between erases!
	if ( (((unsigned int) address) >= 0x1000) &&
	     (((unsigned int) address) <0x1040)  ){// inside infoD?
		FCTL3 = FWKEY; // unlock flash (except for segment A)
		FCTL1 = FWKEY + WRT ; // enable simple write
		*address = value;	// actual write to memory
		FCTL1 = FWKEY ;     // clear write mode
		FCTL3 = FWKEY+LOCK; // relock the segment
	     }
}

//Function to reset panel address in flash mem to broadcast address
void resetAddress(char value, char *address){
	writeDword(value, address);
}
void init_wdt(){
	// setup the watchdog timer as an interval timer
 	WDTCTL =(WDTPW +		// (bits 15-8) password
    	                   	// bit 7=0 => watchdog timer on
      	                 	// bit 6=0 => NMI on rising edge (not used here)
                       	// bit 5=0 => RST/NMI pin does a reset (not used here)
          	 WDTTMSEL +     // (bit 4) select interval timer mode
 		     WDTCNTCL  		// (bit 3) clear watchdog timer counter
 		                	// bit 2=0 => SMCLK is the source
 		                	// bits 1-0 = 00 => source/32K
			 );
    IE1 |= WDTIE;			// enable the WDT interrupt (in the system interrupt register IE1)
}

// =======ADC Initialization and Interrupt Handler========



// Initialization of the ADC
void init_adc(){
  ADC10CTL1= ADC_INCH	//input channel 4
 			  +SHS_0 //use ADC10SC bit to trigger sampling
 			  +ADC10DIV_4 // ADC10 clock/5
 			  +ADC10SSEL_0 // Clock Source=ADC10OSC
 			  +CONSEQ_0; // single channel, single conversion
 			  ;
  ADC10AE0=ADC_INPUT_BIT_MASK; // enable A4 analog input
  ADC10CTL0= SREF_0	//reference voltages are Vss and Vcc
 	          +ADC10SHT_3 //64 ADC10 Clocks for sample and hold time (slowest)
 	          +ADC10ON	//turn on ADC10
 	          +ENC		//enable (but not yet start) conversions
 	          +ADC10IE  //enable interrupts
 	          ;
}


