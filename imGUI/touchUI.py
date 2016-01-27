import kivy
import datetime
import smbus
import time

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label

kivy.require('1.9.0')
from kivy.uix.image import Image

bus = smbus.SMBus(1)
DEVICE1_ADDRESS = 0x50
DEVICE2_ADDRESS = 0x12
DEVICE_REG_MODE1 = 0x00

class Send1Button(Button):
    def on_press(self):
       # now = datetime.datetime.now()
       # self.text = 'minute is ' + str(now.minute)
        bus.write_byte_data(DEVICE1_ADDRESS, DEVICE_REG_MODE1, 4)
        time.sleep(1)
        bus.write_byte(DEVICE1_ADDRESS, 0xFF)
        res = bus.read_byte(DEVICE1_ADDRESS)
        self.text = 'Reading from device address ' + hex(res)
       # time.sleep(4)
       # self.text = 'Toggle LED on MSP430 1'

class Send2Button(Button):
    def on_press(self):
	bus.write_byte_data(DEVICE2_ADDRESS, DEVICE_REG_MODE1, 4)
        time.sleep(1)
        bus.write_byte(DEVICE2_ADDRESS,0xFF)
        res2 = bus.read_byte(DEVICE2_ADDRESS)
        self.text = 'Reading from device address ' + hex(res2)
       # time.sleep(4)
       # self.text = 'Toggle LED on MSP430 2'

class PtWidg(Widget):
    pass


class ptApp(App):
    def build(self):
        return PtWidg()


if __name__ == '__main__':
    ptApp().run()
