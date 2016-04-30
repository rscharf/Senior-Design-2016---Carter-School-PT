import time
import smbus
import os
import fn
import os.path
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Font
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
timings = []
FILE = "/home/pi/newGUIwI2C/SensoryWalk.xlsx"
STATE_0 = 0 #idle, lights and sensor off.  used to reset.
STATE_1 = 1 #initialize, get new address, pass back
STATE_2 = 2 #just listening on sensor
STATE_3 = 3 #lights on, sensors off.  also pass duty cycle for brightness.
PASSWORD = "carterschool21"

class myListItemButton(ListItemButton):
    pass

class myVolSlider(Slider):
    def on_touch_up(self, touch):
        released = super(myVolSlider, self).on_touch_up(touch)
        if released:
            #change volume and play ping
            foo = str(self.value)
            foo = foo[:-2]
            #print foo
            num = int(foo)
            new = fn.changeRange(num, 0, 100, 85, 100)
            print 'num in range is: ' + str(new)
            if (num == 0):
                volstr = "amixer sset 'PCM' 0%"
            else:
                volstr = "amixer sset 'PCM' " + str(new) + "%"
            os.system(volstr)
            os.system('mpg123 /home/pi/newGUIwI2C/bell.mp3 &')

        return released


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
    pass_vol = NumericProperty()
    pass_bright = NumericProperty()
    pass_lang = StringProperty()

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
        self.userKey = fn.reload_dictionary(self.user_dict)
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
            self.pass_vol = self.user_dict[self.sel_usr]['vol']
            self.pass_bright = self.user_dict[self.sel_usr]['bright']
            self.pass_lang = self.user_dict[self.sel_usr]['lang']

class ManageUserProfilesScreen(Screen):
    pass


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
        del self.userKey[:]
        self.user_dict.clear()
        self.userKey = fn.reload_dictionary(self.user_dict)
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
    string_pass = StringProperty()
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
        try:
            self.userKey = fn.reload_dictionary(self.user_dict)
            self.edit_lang = self.user_dict[self.usr_to_edit]['lang']
            self.edit_bright = self.user_dict[self.usr_to_edit]['bright']
            self.edit_vol = self.user_dict[self.usr_to_edit]['vol']
            bus.write_byte_data(0x10, DEVICE_REG_MODE1, STATE_3)
            bus.write_byte_data(0x10, DEVICE_REG_MODE1, int(self.edit_vol))
        except IOError as (errno, strerror):
                #raise e
                print "I/O error({0}): {1}".format(errno, strerror)
                print "write error"

    def OnSliderValueChange(self):
        try:
            val = int(self.brightslide.value)
            bus.write_byte_data(0x10, DEVICE_REG_MODE1, STATE_3)
            bus.write_byte_data(0x10, DEVICE_REG_MODE1, val)
        except IOError as (errno, strerror):
                #raise e
                print "I/O error({0}): {1}".format(errno, strerror)
                print "write error"

    def edit_profile(self):
        f = open("/home/pi/newGUIwI2C/profiles.txt", "r")
        lines = f.readlines()
        f.close()
        f = open("/home/pi/newGUIwI2C/profiles.txt", "w")
        for line in lines:
            if not self.usr_to_edit in line:
                f.write(line)
            if self.usr_to_edit in line:
                f.write(str(self.nameinput.text) + "," + str(self.spinner.text) + "," + str(self.volslide.value) + "," + str(self.brightslide.value) + "\n")
        f.close()
        self.string_pass = str(self.nameinput.text)

    def offLights(self):
        try:
            bus.write_byte_data(0x10, DEVICE_REG_MODE1, STATE_0)
            bus.write_byte_data(0x10, DEVICE_REG_MODE1, 0)
        except IOError as (errno, strerror):
                #raise e
                print "I/O error({0}): {1}".format(errno, strerror)
                print "write error"


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
        del self.userKey[:]
        self.user_dict.clear()
        self.userKey = fn.reload_dictionary(self.user_dict)
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
        f = open("/home/pi/newGUIwI2C/profiles.txt", "r")
        lines = f.readlines()
        f.close()
        f = open("/home/pi/newGUIwI2C/profiles.txt", "w")
        for line in lines:
            if not self.usr_to_del in line:
                f.write(line)
        f.close()

class ProfileDeletedScreen(Screen):
    usr_del = StringProperty()

    def deleteData(self):
        fn.excelDeleteSheet(self.usr_del)

class CreateProfileScreen(Screen):
    spinner = ObjectProperty()
    nameinput = ObjectProperty()
    volslide = ObjectProperty()
    brightslide = ObjectProperty()
    sel_usr = StringProperty()
    yesnocr = StringProperty()
    user_dict = {}
    userKey = ListProperty()


    def OnSliderValueChange(self):
        try:
            val = int(self.brightslide.value)
            bus.write_byte_data(0x10, DEVICE_REG_MODE1, STATE_3)
            bus.write_byte_data(0x10, DEVICE_REG_MODE1, val)
        except IOError as (errno, strerror):
                #raise e
                print "I/O error({0}): {1}".format(errno, strerror)
                print "write error"

    def on_enter(self, *args):
        print('on_enter called for create profile screen')
        del self.userKey[:]
        self.user_dict.clear()
        self.userKey = fn.reload_dictionary(self.user_dict)

    def createprofile(self):
        if str(self.nameinput.text) in self.userKey:
            print('Profile for user ' + str(self.nameinput.text) + ' already exists')
            self.yesnocr = 'already exists'
            self.sel_usr = str(self.nameinput.text)
        #add else if for if there is no user name given or no language given
        elif len(str(self.nameinput.text)) == 0:
            self.yesnocr = 'no user name given'
            self.sel_usr = 'cannot be created'
        else:
            print('Chosen language for user ' + str(self.nameinput.text) + ' is ' + str(self.spinner.text))
            print('Volume set to ' + str(self.volslide.value))
            print('Brightness set to ' + str(self.brightslide.value))
            self.sel_usr = str(self.nameinput.text)
            self.yesnocr = 'has been created'
            f = open("/home/pi/newGUIwI2C/profiles.txt", "a")
            f.write(str(self.nameinput.text) + "," + str(self.spinner.text) + "," + str(self.volslide.value) + "," + str(self.brightslide.value) + "\n")
            f.close()

    def cancelProf(self):
        try:
            self.nameinput.text = ''
            self.spinner.text = 'Select Language'
            self.volslide.value = 0
            self.brightslide.value = 0
            #turn off panel 0 LEDs (showing sample brightness)
            bus.write_byte_data(0x10, DEVICE_REG_MODE1, STATE_0)
            bus.write_byte_data(0x10, DEVICE_REG_MODE1, 0)
        except IOError as (errno, strerror):
                #raise e
                print "I/O error({0}): {1}".format(errno, strerror)
                print "write error"

class ConfirmCreateProfileScreen(Screen):
    usr_create = StringProperty()
    yncreate = StringProperty()

class PanelReplacementScreen(Screen):
    panelToRep = ObjectProperty()
    result_string = StringProperty()
    spinner = ObjectProperty()
    passinput = ObjectProperty()

    def panelConnected(self):
        try:
            if self.passinput.text == PASSWORD:
                #python I2C code goes here to send actual address
                #send MSP430 state var then send new address
                try:
                    self.panelToRep = int(self.spinner.text)
                except ValueError:
                    self.result_string = 'Error: select a panel number'
                bus.write_byte_data(BROADCAST_ADDR, DEVICE_REG_MODE1, STATE_1)
                bus.write_byte_data(BROADCAST_ADDR, DEVICE_REG_MODE1, new_addr[self.panelToRep])
                    
                time.sleep(1)

                #read new address back from MSP430
                backAddr = bus.read_byte(new_addr[self.panelToRep])
                    
                if (backAddr == new_addr[self.panelToRep]):
                    #update label for GUI
                    self.result_string = 'Panel Succesfully Connected'
                else:
                    #display error with what was received
                    self.result_string = 'Error'
            else:
                self.result_string = "Invalid password!"
        except IOError as (errno, strerror):
                #raise e
                print "I/O error({0}): {1}".format(errno, strerror)
                print "write error"

    def cancelButt(self):
        self.passinput.text = ''
        self.spinner.text = '#'
        self.result_string = ''

class FinishRunScreen(Screen):
    user_save = StringProperty()

    def saveData(self):
        #put excel stuff here.  For now, just print out the list
        print "For run on " + time.strftime("%m/%d/%Y") + " at " + time.strftime("%I:%M:%S %p")
        print(timings)
        print "Number of feet reached is " + str(len(timings))

        fn.excelDataSave(self.user_save, timings)

class DataSavedScreen(Screen):
    pass

class ExportDataScreen(Screen):
    removestr = StringProperty()

    def exportButt(self):
        self.removestr = ''
        os.system('sh /home/pi/newGUIwI2C/export.sh')
        self.removestr = 'Now safe to remove flash drive'

    def backButt(self):
        self.removestr = ''    

class ConfirmDeleteDataScreen(Screen):
    usr_name = StringProperty()

class RunningScreen(Screen):
    footMarkerStr = StringProperty()
    footNum = NumericProperty()
    user_name_text = StringProperty()
    current_panel = NumericProperty()
    sent_active_panel = None
    bright_val = NumericProperty()
    vol_val = NumericProperty()
    bright_send = None
    language = StringProperty()

    start_time = None
    end_time = None

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
        try:
            for num in range(self.current_panel-1, -1, -1):
                bus.write_byte_data(new_addr[num], DEVICE_REG_MODE1, STATE_0)
                bus.write_byte_data(new_addr[num], DEVICE_REG_MODE1, 0)
            self.current_panel = 0
        except IOError as (errno, strerror):
                #raise e
                print "I/O error({0}): {1}".format(errno, strerror)
                print "write error"


    def on_enter(self, *args):
        self.sent_active_panel = False
        self.footNum = 0
        self.current_panel = 0
        #set the volume for the current user
        foo = str(self.vol_val)
        foo = foo[:-2]
        num = int(foo)
        new = fn.changeRange(num, 0, 100, 85, 100)
        print 'num in range is: ' + str(new)
        if (num == 0):
            volstr = "amixer sset 'PCM' 0%"
        else:
            volstr = "amixer sset 'PCM' " + str(new) + "%"
        os.system(volstr)
        #also edit brightness value to send over I2C
        temp = str(self.bright_val)
        temp = temp[:-2]
        self.bright_send = int(temp)


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
            if self.current_panel < 21:
                try:
                    bus.write_byte_data(new_addr[self.current_panel], DEVICE_REG_MODE1, STATE_2)
                    bus.write_byte_data(new_addr[self.current_panel], DEVICE_REG_MODE1, 0) #temp, delete later

                    self.sent_active_panel = True
                except IOError as (errno, strerror):
                    #raise e
                    print "I/O error({0}): {1}".format(errno, strerror)
                    print "write error"
        else:
            if self.current_panel < 21:
                try:
                    result = bus.read_byte(new_addr[self.current_panel])
                    if result == 1:

                        bus.write_byte_data(new_addr[self.current_panel], DEVICE_REG_MODE1, STATE_3)
                        bus.write_byte_data(new_addr[self.current_panel], DEVICE_REG_MODE1, self.bright_send) #number will change to the value in the brightness setting, this is the duty cycle out of 100 for PWM

                        print ("RESULT IS 1!!!!")

                        self.sent_active_panel = False

                        if self.current_panel == 0:
                            #make sure we're starting a new array of timings
                            del timings[:]
                            self.start_time = time.time()                        
                        #need to add here some kind of statement eventually that says it can only go to panel 20
                        if self.current_panel > 0:
                            self.footNum += 1
                            self.end_time = time.time()
                            elapsed = self.end_time - self.start_time
                            timings.append(round(elapsed, 2))
                            self.start_time = self.end_time
                            print ("current_panel is > 1")
                            if (self.footNum == 1):
                                self.footMarkerStr = str(self.footNum) + ' foot'
                            else:
                                self.footMarkerStr = str(self.footNum) + ' feet'

                            print('working - ' + str(self.footNum))

                        soundStr = fn.toPlay(self.current_panel, self.language)
                        os.system(soundStr)
                        self.current_panel += 1
                        print ("current_panel incremented")
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
