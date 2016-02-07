from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider


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

class AdjustVolumeScreen(Screen):
    pass


class CreateProfileScreen(Screen):
    spinner = ObjectProperty()
    nameinput = ObjectProperty()
    volslide = ObjectProperty()
    brightslide = ObjectProperty()

    def createprofile(self):
        print('Chosen language for user', self.nameinput.text, 'is', self.spinner.text)
        print('Volume set to', self.volslide.value)
        print('Brightness set to', self.brightslide.value)

    def cancelProf(self):
        self.nameinput.text = ''
        self.spinner.text = 'Select Language'
        self.volslide.value = 0
        self.brightslide.value = 0

class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file("screen.kv")

class MainApp(App):
    def build(self):
        return presentation

if __name__ == '__main__':
    MainApp().run()