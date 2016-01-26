import kivy
import datetime

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label

kivy.require('1.9.0')
from kivy.uix.image import Image


class SendButton(Button):
    def on_press(self):
        now = datetime.datetime.now()
        self.text = 'minute is ' + str(now.minute)


class PtWidg(Widget):
    pass


class ptApp(App):
    def build(self):
        return PtWidg()


if __name__ == '__main__':
    ptApp().run()