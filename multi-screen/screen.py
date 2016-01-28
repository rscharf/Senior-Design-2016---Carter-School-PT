from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

class HomeScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class StartUserRunScreen(Screen):
    pass

class ManageUserProfilesScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file("screen.kv")

class MainApp(App):
    def build(self):
        return presentation

MainApp().run()