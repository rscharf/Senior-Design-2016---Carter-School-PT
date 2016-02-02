from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen

class HomeScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class StartUserRunScreen(Screen):
    pass

class ManageUserProfilesScreen(Screen):
    pass

class InitialPanelConfigScreen(Screen):
    pass

class AdjustVolumeScreen(Screen):
    pass

class CreateProfileScreen(Screen):
    pass
    #textinput = TextInput(text='Hello world')

class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file("screen.kv")

class MainApp(App):
    def build(self):
        return presentation

MainApp().run()