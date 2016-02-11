import time
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
            self.panelNo += 1
            self.panel_connect = 'Connect Panel: ' + str(self.panelNo)

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

    def __init__(self, **kwargs):
        super(RunningScreen, self).__init__(**kwargs)
        self.footNum = 0
        if (self.footNum == 1):
            self.footMarkerStr = str(self.footNum) + ' foot'
        else:
            self.footMarkerStr = str(self.footNum) + ' feet'


    def startScreen(self):
        #schedule timer to check for i2c data
        Clock.schedule_interval(self.startRun,1)

    def cancelButt(self):
        Clock.unschedule(self.startRun, all=True)
        self.footNum = 0
        self.footMarkerStr = str(self.footNum) + ' feet'

    def startRun(self, dt):
        #python i2c here for detecting sensor triggers and giving acks back for turning on lights, trigger sound

        #update on screen labels
        self.footNum+=1
        if (self.footNum == 1):
            self.footMarkerStr = str(self.footNum) + ' foot'
        else:
            self.footMarkerStr = str(self.footNum) + ' feet'

        print('working - ' + str(self.footNum))



class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file("screen.kv")

class MainApp(App):
    def build(self):
        return presentation

if __name__ == '__main__':
    MainApp().run()