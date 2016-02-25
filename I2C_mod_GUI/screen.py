import time
import smbus
import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, NumericProperty, ReferenceListProperty
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


class myListItemButton(ListItemButton):
    pass


class HomeScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class StartUserRunScreen(Screen):
    user_dict = {}
    userKey = ListProperty()
    users_list = ListView()
    button_text = StringProperty()
    sel_usr = StringProperty()
    def __init__(self, **kwargs):
        super(StartUserRunScreen, self).__init__(**kwargs)
        self.button_text = 'Select User to Start Run'
        self.sel_usr = 'No user selected'

    def on_enter(self, *args):
        print('on enter called for start user run screen')
        self.button_text = 'Select User to Start Run'
        self.sel_usr = 'No user selected'
        del self.userKey[:]
        self.user_dict.clear()
        reload_dictionary(self.user_dict, self.userKey)
        if self.userKey != None:
            list_adapter = ListAdapter(data=self.userKey, selection_mode='single', allow_empty_selection=True, cls=myListItemButton)
        self.users_list.adapter = list_adapter
        self.users_list.adapter.bind(on_selection_change=self.callback)
        self.users_list._trigger_reset_populate()

    def callback(self, adapter):
        if len(adapter.selection) == 0:
            self.button_text = 'Select User to Start Run'
            self.sel_usr = 'No user selected'
            print "No selected item"
        else:
            print adapter.selection[0].text
            self.sel_usr = adapter.selection[0].text
            self.button_text = 'Start run for ' + adapter.selection[0].text

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

class EditProfileScreen(Screen):
    user_dict = {}
    userKey = ListProperty()
    users_list = ListView()
    sel_usr = StringProperty()

    def __init__(self, **kwargs):
        super(EditProfileScreen, self).__init__(**kwargs)
        self.sel_usr = 'No user selected'

    def on_enter(self, *args):
        print('on_enter called for edit profile screen')
        #self.sel_usr = 'No user selected'
        del self.userKey[:]
        self.user_dict.clear()
        reload_dictionary(self.user_dict, self.userKey)
        if self.userKey != None:
            list_adapter = ListAdapter(data=self.userKey, selection_mode='single', allow_empty_selection=False, cls=myListItemButton)
        self.sel_usr = self.userKey[0]
        self.users_list.adapter = list_adapter
        self.users_list.adapter.bind(on_selection_change=self.callback)
        self.users_list._trigger_reset_populate()

    def callback(self, adapter):
        if len(adapter.selection) == 0:
            self.sel_usr = 'No user selected'
            print "No selected item"
        else:
            print adapter.selection[0].text
            self.sel_usr = adapter.selection[0].text

class ProfileEditingScreen(Screen):
    usr_to_edit = StringProperty()
    user_dict = {}
    userKey = ListProperty()
    edit_lang = StringProperty()
    edit_vol = NumericProperty()
    edit_bright = NumericProperty()

    spinner = ObjectProperty()
    nameinput = ObjectProperty()
    volslide = ObjectProperty()
    brightslide = ObjectProperty()
    def on_enter(self, *args):
        reload_dictionary(self.user_dict, self.userKey)
        self.edit_lang = self.user_dict[self.usr_to_edit]['lang']
        self.edit_bright = self.user_dict[self.usr_to_edit]['bright']
        self.edit_vol = self.user_dict[self.usr_to_edit]['vol']

    def edit_profile(self):
        f = open("profiles.txt", "r")
        lines = f.readlines()
        f.close()
        f = open("profiles.txt", "w")
        for line in lines:
            if not self.usr_to_edit in line:
                f.write(line)
            if self.usr_to_edit in line:
                f.write(str(self.nameinput.text) + "," + str(self.spinner.text) + "," + str(self.volslide.value) + "," + str(self.brightslide.value) + "\n")
        f.close()


class ConfirmEditScreen(Screen):
    usr_edit = StringProperty()

class DeleteProfileScreen(Screen):
    user_dict = {}
    userKey = ListProperty()
    users_list = ListView()
    sel_usr = StringProperty()

    def __init__(self, **kwargs):
        super(DeleteProfileScreen, self).__init__(**kwargs)
        self.sel_usr = 'No user selected'

    def on_enter(self, *args):
        print('on_enter called for delete profile screen')
        #self.sel_usr = 'No user selected'
        del self.userKey[:]
        self.user_dict.clear()
        reload_dictionary(self.user_dict, self.userKey)
        if self.userKey != None:
            list_adapter = ListAdapter(data=self.userKey, selection_mode='single', allow_empty_selection=False, cls=myListItemButton)
        self.sel_usr = self.userKey[0]
        self.users_list.adapter = list_adapter
        self.users_list.adapter.bind(on_selection_change=self.callback)
        self.users_list._trigger_reset_populate()

    def callback(self, adapter):
        if len(adapter.selection) == 0:
            self.sel_usr = 'No user selected'
            print "No selected item"
        else:
            print adapter.selection[0].text
            self.sel_usr = adapter.selection[0].text

class ConfirmDeleteScreen(Screen):
    usr_to_del = StringProperty()

    def deleteUser(self):
        f = open("profiles.txt", "r")
        lines = f.readlines()
        f.close()
        f = open("profiles.txt", "w")
        for line in lines:
            if not self.usr_to_del in line:
                f.write(line)
        f.close()

class ProfileDeletedScreen(Screen):
    usr_del = StringProperty()

class CreateProfileScreen(Screen):
    spinner = ObjectProperty()
    nameinput = ObjectProperty()
    volslide = ObjectProperty()
    brightslide = ObjectProperty()
    sel_usr = StringProperty()
    yesnocr = StringProperty()
    user_dict = {}
    userKey = ListProperty()

    def on_enter(self, *args):
        print('on_enter called for create profile screen')
        del self.userKey[:]
        self.user_dict.clear()
        reload_dictionary(self.user_dict, self.userKey)

    def createprofile(self):
        if str(self.nameinput.text) in self.userKey:
            print('Profile for user ' + str(self.nameinput.text) + ' already exists')
            self.yesnocr = 'already exists'
            self.sel_usr = str(self.nameinput.text)
        else:
            print('Chosen language for user ' + str(self.nameinput.text) + ' is ' + str(self.spinner.text))
            print('Volume set to ' + str(self.volslide.value))
            print('Brightness set to ' + str(self.brightslide.value))
            self.sel_usr = str(self.nameinput.text)
            self.yesnocr = 'has been created'
            f = open("profiles.txt", "a")
            f.write(str(self.nameinput.text) + "," + str(self.spinner.text) + "," + str(self.volslide.value) + "," + str(self.brightslide.value) + "\n")
            f.close()

    def cancelProf(self):
        self.nameinput.text = ''
        self.spinner.text = 'Select Language'
        self.volslide.value = 0
        self.brightslide.value = 0

class ConfirmCreateProfileScreen(Screen):
    usr_create = StringProperty()
    yncreate = StringProperty()

class PanelReplacementScreen(Screen):
    panelToRep = ObjectProperty()

class RunningScreen(Screen):
    footMarkerStr = StringProperty()
    footNum = NumericProperty()
    user_name_text = StringProperty()
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

    def finishRun(self):
        for num in range(self.current_panel-1, -1, -1):
            bus.write_byte_data(new_addr[num], DEVICE_REG_MODE1, 0)
            bus.write_byte_data(new_addr[num], DEVICE_REG_MODE1, 0)
        self.current_panel = 0


    def on_enter(self, *args):
        self.sent_active_panel = False
        self.footNum = 0
        self.current_panel = 0

    def startScreen(self):
        #schedule timer to check for i2c data
        Clock.schedule_interval(self.startRun,0.1)

    def cancelButt(self):
        Clock.unschedule(self.startRun, all=True)
        self.footNum = 0
        self.footMarkerStr = str(self.footNum) + ' feet'

    def startRun(self, dt):
        #python i2c here for detecting sensor triggers and giving acks back for turning on lights, trigger sound

       
        if self.sent_active_panel == False:
            try:
                bus.write_byte_data(new_addr[self.current_panel], DEVICE_REG_MODE1, 2) #change back to 2 for final state
                bus.write_byte_data(new_addr[self.current_panel], DEVICE_REG_MODE1, 0) #temp, delete later

                self.sent_active_panel = True
            except IOError as (errno, strerror):
                #raise e
                print "I/O error({0}): {1}".format(errno, strerror)
                print "write error"
        else:
            try:
                #time.sleep(0.01)
                result = bus.read_byte(new_addr[self.current_panel])
                if result == 1:
                    bus.write_byte_data(new_addr[self.current_panel], DEVICE_REG_MODE1, 3)
                    bus.write_byte_data(new_addr[self.current_panel], DEVICE_REG_MODE1, 0)
                    print ("RESULT IS 1!!!!")
                    self.sent_active_panel = False
                    self.current_panel += 1
                    print ("current_panel incremented")
                    if self.current_panel == 1:
                        os.system('mpg123 startuserrun.mp3 &')
                    #need to add here some kind of statement eventually that says it can only go to panel 20
                    if self.current_panel > 1:
                        self.footNum += 1
                        if self.current_panel == 2:
                            os.system('mpg123 one.mp3 &')
                        if self.current_panel == 3:
                            os.system('mpg123 two.mp3 &')
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



class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file("screen.kv")

class MainApp(App):
    def build(self):
        return presentation

if __name__ == '__main__':
    MainApp().run()
