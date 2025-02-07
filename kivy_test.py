import threading
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

from BTUtils import scan_bt

def on_bt_button_click(*args):
    print('BT scan button clicked!')
    scan_thread = threading.Thread(target=scan_bt)
    try:
        scan_thread.start()
    except Exception as e:
        print(f'Error starting scan thread: {e}')

def on_button_click(*args):
    print('Button clicked, it worked!')

class MyApp(App):
    def build(self):
        fl = FloatLayout()
        box = BoxLayout(orientation='vertical')
        Label(text='BT test!')
        box.add_widget(Label(text='BT test!'))
        button = Button(text='Start BT discovery', size_hint=(.5, .5), pos=(100, 100))
        button.bind(on_press=on_bt_button_click)
        box.add_widget(button)
        button_1 = Button(text='Does this work?', size_hint=(.5, .5), pos=(100, 100))
        button_1.bind(on_press=on_button_click)
        box.add_widget(button_1)
        fl.add_widget(box)
        return fl

if __name__ == '__main__':
    MyApp().run()