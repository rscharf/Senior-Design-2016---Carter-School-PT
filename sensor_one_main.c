/* 10-30-13
 * This is an example of using the ADC to convert a single
 * analog input. The external input is to ADC10 channel A4.
 * This version triggers a conversion with regular WDT interrupts and
 * uses the ADC10 interrupt to copy the converted value to a variable in memory.
*/

#include "msp430g2553.h"

// Define bit masks for ADC pin and channel used as P1.4
#define ADC_INPUT_BIT_MASK 0x10
#define ADC_INCH INCH_4
#define BJT_OUT	4
#define COM_IN 0x20
#define RESET_BUTT 8

#define IR_THRESHOLD	70

 /* declarations of functions defined later */
 void init_adc(void);
 void init_wdt(void);

// =======ADC Initialization and Interrupt Handler========

// Global variables that store the results (read from the debugger)
 volatile int latest_result;   // most recent result is stored in latest_result
 //volatile unsigned long conversion_count=0; //total number of conversions done
 volatile int adc_vals_before_ave = 0;
 volatile int adc_average = 0;
 volatile int adc_average_add = 0;
 volatile int adc_vals_array[5];
 volatile unsigned char last_button;

/*
 * The ADC handler is invoked when a conversion is complete.
 * Its action here is to simply store the result in memory.
 */
 void interrupt adc_handler(){
	 latest_result=ADC10MEM;   // store the answer
 }
 ISR_VECTOR(adc_handler, ".int05")

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


 // ===== Watchdog Timer Interrupt Handler =====
interrupt void WDT_interval_handler(){
		ADC10CTL0 |= ADC10SC;  // trigger a conversion

		//button handling
				unsigned char b;
				b= (P1IN & RESET_BUTT);  // read the BUTTON bit
				if (last_button && (b==0))
				{ // has the button bit gone from high to low
				  //turn off LEDs and reset COM_OUT to low
					P1OUT &= ~0x01;
					P1OUT &= ~BJT_OUT;
				}
				last_button=b;    // remember button reading for next time.

		unsigned char com_in_val;
		com_in_val = (P1IN & COM_IN);
		//com_in_last = com_in_val;

		if (com_in_val == 0)
		{
			P1OUT &= ~0x01;
			P1OUT &= ~BJT_OUT;
		}

		int j;
		for (j=0; j<5; j++)
		{
			adc_average_add = adc_average_add + adc_vals_array[j];
		}
		adc_average = adc_average_add/5;
		adc_average_add = 0;

		if ((adc_average > IR_THRESHOLD) && (com_in_val !=0))
		{
			P1OUT |= 0x01;
			P1OUT |= BJT_OUT;
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
ISR_VECTOR(WDT_interval_handler, ".int10")

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

/*
 * The main program just initializes everything and leaves the action to
 * the interrupt handlers!
 */

void main(){

	WDTCTL = WDTPW + WDTHOLD;       // Stop watchdog timer
	BCSCTL1 = CALBC1_8MHZ;			// 8Mhz calibration for clock
  	DCOCTL  = CALDCO_8MHZ;

  	init_adc();
  	init_wdt();

  	P1DIR |= 0x01;
  	P1DIR |= BJT_OUT;
  	P1DIR &= ~COM_IN; //set p1.5 as input from sensor_zero
  	P1DIR &= ~RESET_BUTT;

  	P1OUT |= RESET_BUTT;
  	P1REN |= RESET_BUTT;

	_bis_SR_register(GIE+LPM0_bits);
}
