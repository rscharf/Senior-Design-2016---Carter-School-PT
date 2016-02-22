import time
import smbus
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, NumericProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListView, ListItemButton

#Global Variables
bus = smbus.SMBus(1)
BROADCAST_ADDR = 0x7F
DEVICE_REG_MODE1 = 0X00
new_addr = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24]


def reload_dictionary(user_dict, userKey):
    with open("profiles.txt") as f:
        for line in f:
            (name, lang, vol, bright) = line.split(',',4)
            user_dict[name] = {'name': name, 'lang': lang, 'vol': float(vol), 'bright': float(bright)}
            userKey.append(name)
    f.close()
    userKey = ListProperty(user_dict.keys())
    #userKey.sort()

class HomeScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class StartUserRunScreen(Screen):
    user_dict = {}
    userKey = ListProperty()
    users_list = ListView()
    def on_enter(self, *args):
        reload_dictionary(self.user_dict, self.userKey)
        if self.userKey != None:
            list_adapter = ListAdapter(data=self.userKey, selection_mode='single', allow_empty_selection=True, cls=ListItemButton)
        self.users_list.adapter = list_adapter
        self.users_list.adapter.bind(on_selection_change=self.callback)

    def callback(self, adapter):
        if len(adapter.selection) == 0:
            print "No selected item"
        else:
            print adapter.selection[0].text

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
            
            time.sleep(1)

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
        self.panelNo = 0
        self.panel_connect = 'Connect Panel: ' + str(self.panelNo)

class CreateProfileScreen(Screen):
    spinner = ObjectProperty()
    nameinput = ObjectProperty()
    volslide = ObjectProperty()
    brightslide = ObjectProperty()

    def createprofile(self):
        print('Chosen language for user ' + str(self.nameinput.text) + ' is ' + str(self.spinner.text))
        print('Volume set to ' + str(self.volslide.value))
        print('Brightness set to ' + str(self.brightslide.value))

        f = open("profiles.txt", "a")
        f.write(str(self.nameinput.text) + ", " + str(self.spinner.text) + ", " + str(self.volslide.value) + ", " + str(self.brightslide.value) + "\n")
        f.close()

    def cancelProf(self):
        self.nameinput.text = ''
        self.spinner.text = 'Select Language'
        self.volslide.value = 0
        self.brightslide.value = 0

class RunningScreen(Screen):
    footMarkerStr = StringProperty()
    footNum = NumericProperty()
    current_panel = NumericProperty()
    sent_active_panel = None

    def __init__(self, **kwargs):
        super(RunningScreen, self).__init__(**kwargs)
        self.footNum = 0
        self.current_panel = 0
        self.sent_active_panel = False

        if (self.footNum == 1):
            self.footMarkerStr = str(self.footNum) + ' foot'
        else:
            self.footMarkerStr = str(self.footNum) + ' feet'


    def startScreen(self):
        #schedule timer to check for i2c data
        Clock.schedule_interval(self.startRun,.01)

    def cancelButt(self):
        Clock.unschedule(self.startRun, all=True)
        self.footNum = 0
        self.footMarkerStr = str(self.footNum) + ' feet'

    def startRun(self, dt):
        #python i2c here for detecting sensor triggers and giving acks back for turning on lights, trigger sound
        
        if self.sent_active_panel == False:
            try:
                bus.write_byte_data(new_addr[self.current_panel], DEVICE_REG_MODE1, 4) #change back to 2 for final state
                bus.write_byte_data(new_addr[self.current_panel], DEVICE_REG_MODE1, 0) #temp, delete later
                #bus.write_byte_data(BROADCAST_ADDR, DEVICE_REG_MODE1, 4)
                #bus.write_byte_data(BROADCAST_ADDR, DEVICE_REG_MODE1, 0)
                self.sent_active_panel = True
            except IOError as (errno, strerror):
                #raise e
                print "I/O error({0}): {1}".format(errno, strerror)
                print "write error"
        else:
            try:
                time.sleep(1)
                result = bus.read_byte(new_addr[self.current_panel])
                if result == 1:
                    print ("RESULT IS 1!!!!")
                    self.sent_active_panel = False
                    self.current_panel += 1
                    print ("current_panel incremented")
                    if self.current_panel > 1:
                        self.footNum += 1
                        print ("current_panel is > 1")
                        if (self.footNum == 1):
                            self.footMarkerStr = str(self.footNum) + ' foot'
                        else:
                            self.footMarkerStr = str(self.footNum) + ' feet'

                        print('working - ' + str(self.footNum))
                else:
                    print ('result not 1')
            except IOError as (errno, strerror):
                #raise e
                print "I/O error({0}): {1}".format(errno, strerror)
                print "read error"

        #update on screen labels if sensor triggered is > 0
        #self.footNum+=1
       # if (self.footNum == 1):
       #     self.footMarkerStr = str(self.footNum) + ' foot'
       # else:
       #     self.footMarkerStr = str(self.footNum) + ' feet'

       # print('working - ' + str(self.footNum))



class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file("screen.kv")

class MainApp(App):
    def build(self):
        return presentation

if __name__ == '__main__':
    MainApp().run()
