#ifndef TI_USCI_I2C_SLAVE
#define TI_USCI_I2C_SLAVE


// Define pins for SDA and SCL
#define SDA_PIN BIT7                                 // P1.7
#define SCL_PIN BIT6                                 // P1.6
#define RED 0x01									 // P1.0 - Red LED

// Define bit masks for ADC pin and channel used as P1.4
#define ADC_INPUT_BIT_MASK 0x10
#define ADC_INCH INCH_4
#define BJT_OUT	4
#define BUTTON BIT3
#define IR_THRESHOLD	70


//Function Declarations
void TI_USCI_I2C_slaveinit(void (*SCallback)(unsigned char volatile *value),
                           void (*TCallback)(unsigned char volatile *value),
                           void (*RCallback)(unsigned char value),
                           unsigned char slave_address);
void eraseD();
void writeDword(char value, char *address);
void resetAddress(char value, char *address);
void init_adc(void);
void init_wdt(void);




#endif
