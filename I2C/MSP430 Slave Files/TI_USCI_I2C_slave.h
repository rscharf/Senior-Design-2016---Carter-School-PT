#ifndef TI_USCI_I2C_SLAVE
#define TI_USCI_I2C_SLAVE

#define SDA_PIN BIT7                                 // P1.7
#define SCL_PIN BIT6                                 // P1.6
#define RED 0x01									 // P1.0 - Red LED
void TI_USCI_I2C_slaveinit(void (*SCallback)(unsigned char volatile *value),
                           void (*TCallback)(unsigned char volatile *value),
                           void (*RCallback)(unsigned char value),
                           unsigned char slave_address);
void eraseD();
void writeDword(char value, char *address);


#endif
