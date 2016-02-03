import smbus

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty

#Global Variables
bus = smbus.SMBus(1)
BROADCAST_ADDR = 0x7F
DEVICE_REG_MODE1 = 0X00
new_addr = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24]


class HomeScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class StartUserRunScreen(Screen):
    pass

class ManageUserProfilesScreen(Screen):
    pass

class InitialPanelConfigScreen(Screen):
    panel_connect = StringProperty()
    panelNo = 0

    def __init__(self, **kwargs):
        super(InitialPanelConfigScreen, self).__init__(**kwargs)
        self.panel_connect = 'Connect Panel: ' + str(self.panelNo)

    def panelConnected(self):
        #python I2C code goes here to send actual address
        if self.panelNo < 20:
            #send MSP430 state var then send new address
            bus.write_byte_data(BROADCAST_ADDR, DEVICE_REG_MODE1, 1)
            bus.write_byte_data(BROADCAST_ADDR, DEVICE_REG_MODE1, new_addr[self.panelNo])
            
            #read new address back from MSP430
            backAddr = bus.read_byte(new_addr[self.panelNo])
            
            if (backAddr == new_addr[self.panelNo]):
                #update label for GUI
                self.panelNo += 1
                self.panel_connect = 'Connect Panel: ' + str(self.panelNo)
            else:
                #display error with what was received
                self.panel_connect = 'Error: did not receive address back.  Received: ' + str(backAddr)

    def cancelButton(self):
        #app.root.current = 'settings'
        self.panelNo = 0
        self.panel_connect = 'Connect Panel: ' + str(self.panelNo)

class AdjustVolumeScreen(Screen):
    pass

class CreateProfileScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file("screen.kv")

class MainApp(App):
    def build(self):
        return presentation

if __name__ == '__main__':
    MainApp().run()
