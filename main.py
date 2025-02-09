# Copyright (C) 2024  Stas@childsplay.mobi
# Copyright (C) 2024  BraintrainerPlus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = 'stas Zytkiewicz stas@childsplay.mobi'

import os
import subprocess
import threading
import time
#### Applies BTP specific styling for kivy widgets ######
from os import environ

from audio import PulseInfo

environ['KIVY_LOG_MODE'] = 'PYTHON'

##########################################################
from Style import StyleBase
from kivy.config import Config

if 'DEBUG' not in environ.keys():
    Config.set('graphics', 'fullscreen', 'auto')
else:
    Config.set('modules', 'inspector', 1)

from threading import Thread

from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.label import Label

import SPLogging
SPLogging.set_level('debug')
SPLogging.start()
import logging

from utils import set_locale
set_locale()

from BTUtils import BTadapter

class Observer:
    """Observer that will implement the following methods:
    on_device_added
    on_device_removed
    on_device_connected
    on_device_disconnected
    Used by BTadapter to notify the observer when a device is added or removed.
    """
    def __init__(self, parent):
        self.logger = logging.getLogger("bt.Observer")
        self.parent = parent

    @mainthread
    def on_device_added(self, device):
        self.logger.debug(f"Device added: {device!r}")
        self.parent.add_device_to_list(device)

    def on_device_removed(self, device):
        pass

    def on_device_connected(self, device):
        pass

    def on_device_disconnected(self, device):
        pass

class BTDeviceListItem(ToggleButton):
    """Build by main.kv"""
    text_connect = StringProperty(_("Connect"))
    text_connected = StringProperty(_("Connected"))
    text_connecting = StringProperty(_("Connecting..."))
    text_disconnecting = StringProperty(_("Disconnecting..."))

    def __init__(self, device_id, device):
        super(BTDeviceListItem, self).__init__()
        self.logger = logging.getLogger("bt.BTDeviceListItem")
        self.text = device.Alias
        self.logger.info(f"Creating BTDeviceListItem with text: {self.text}")
        self.device = device
        self.device_path = device.device_path
        if self.device.connected:
            self.state = "down"
            self.text = f"{self.device.Alias} - {self.text_connected}"

    def _device_connect(self, bt_device_list_item):
        if bt_device_list_item.state == "down":
            self.logger.info(f"Connecting to BT device: {self.device.Alias}")
            i = 0
            while i < 2:
                try:
                    self.device.connect()
                except Exception as e:
                    self.logger.warning(f"Failed to connect to BT device: {self.device.Alias}")
                    self.logger.warning(f"Error: {e}, retrying after 1 second...")
                    i += 1
                    time.sleep(1)
                else:
                    self.text = f"{self.device.Alias} - {self.text_connected}"
                    break
            if i >= 2:
                self.logger.error(f"Failed to connect to BT device: {self.device.Alias}")
                bt_device_list_item.state = "normal"
                self.text = self.device.Alias
                self.device.disconnect()
        else:
            self.logger.info(f"Disconnecting from BT device: {self.device.Alias}")
            self.device.disconnect()
            bt_device_list_item.state = "normal"
            self.text = self.device.Alias


    def on_bt_device_list_item_clicked(self, bt_device_list_item):
        self.logger.info(f"BT device list item clicked: {bt_device_list_item.text}")
        Clock.schedule_once(lambda dt: self._device_connect(bt_device_list_item))
        if bt_device_list_item.state == "down":
            self.text = self.text_connecting
        else:
            self.text = self.device.Alias

class MyToggleButton(ToggleButton):
    def __init__(self, **kwargs):
        super(MyToggleButton, self).__init__(**kwargs)
        self.sink = None
        self.pi = PulseInfo()

    def on_state(self, instance, value):
        if not hasattr(self, "pi"):
            # This is called before the object is fully initialized in AudioContent.fill_grid
            return
        if value == "down":
            print(self.sink)
            self.pi.set_default_sink(self.sink['sink_name'])

class AudioContent(BoxLayout):
    """Build by main.kv"""
    text_audio = StringProperty(_("Choose the audio output"))
    text_close = StringProperty(_("Close"))

    def __init__(self):
        super(AudioContent, self).__init__()
        self.logger = logging.getLogger("bt.AudioContent")
        self.pulse_info = PulseInfo()

        self.sinks = self.pulse_info.get_sinks()
        self.default_sink = self.pulse_info.get_default_sink()
        self.fill_grid()

    def fill_grid(self):
        self.logger.info("Fill grid")
        for name, sink in self.sinks.items():
            print(name, sink)
            tb = MyToggleButton(text=name, group="audio", state="down" if name in self.default_sink else "normal")
            tb.sink = sink
            self.ids.audio_grid.add_widget(tb)


class Main(BoxLayout):
    """Build by main.kv"""

    text_header_list = StringProperty(_("Bluetooth Devices"))
    text_close = StringProperty(_("Close"))
    text_scan = StringProperty(_("Find BT devices"))
    text_progress = StringProperty(_("Scanning for BT devices"))
    text_reset_bt = StringProperty(_("Reset BT adapter"))
    text_start_audio = StringProperty(_("Set audio"))

    def __init__(self):
        super(Main, self).__init__()
        self.logger = logging.getLogger("bt.Main")
        self.we_have_bt = False
        if self._check_for_bluetooth():
            self.observer = Observer(parent=self)
            self.bt_adapter = BTadapter(observer=self.observer)
            self.scan_duration = 5 # seconds
            self.on_scan_button_clicked()


    def _check_for_bluetooth(self):
        """Check if the bluetooth adapter is available.
        If not we disable the buttons scan_button and reset_button and enable the audio_button"""
        self.logger.info("Check for bluetooth")
        cmd = '/usr/bin/hciconfig up'
        try:
            subprocess.run(cmd.split(), check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to check for bluetooth: {e}")
            self.ids.scan_button.disabled = True
            self.ids.reset_button.disabled = True
            self.ids.audio_button.disabled = False

            lbl = Label(text=_("Bluetooth adapter not found\nOnly audio settings available!"),
                        size_hint=(1, None), halign="center", valign="middle",
                        font_size='36sp', color=(1, 0, 0, 1))
            self.ids.bt_devices_grid.add_widget(lbl)
            return False
        else:
            self.we_have_bt = True
            return True

    def _update_progressbar(self, *args):
        self.ids.progress_bar.value += 100 / (self.scan_duration * 2)
        if self.ids.progress_bar.value >= 100:
            self.ids.progress_bar.value = 100

    def get_existing_devices(self):
        self.logger.info("Get existing BT devices")
        for device in self.bt_adapter.get_all_devices().values():
            self.add_device_to_list(device)

    def add_device_to_list(self, device):
        self.logger.info(f"Add BT device to layout: {device.Alias}")
        # make sure we don't add the same device twice
        for child in self.ids.bt_devices_grid.children:
            if child.device_path == device.device_path:
                return
        self.ids.bt_devices_grid.add_widget(BTDeviceListItem(device.Alias, device))


    def on_close_button_clicked(self):
        self.logger.info("Close button clicked")
        # In case we have a onscreen keyboard
        Window.release_all_keyboards()
        App.get_running_app().stop()


    def on_scan_button_clicked(self):
        self.logger.info("Scan button clicked")
        self.ids.progress_bar.value = 0
        self.ids.bt_devices_grid.clear_widgets()
        self.ids.audio_button.disabled = True
        self.get_existing_devices()

        def start_scan(*args):
            self.bt_adapter.scan_adapter(scan_duration=self.scan_duration)
            Clock.unschedule(self._update_progressbar)
            self.ids.progress_bar.value = 100
            self.ids.text_progress.text = _("Scanning finished")
            self.ids.audio_button.disabled = False

        thr = Thread(target=start_scan)
        thr.start()
        Clock.schedule_interval(self._update_progressbar, 0.5)

    def on_audio_button_clicked(self):
        self.logger.info("Audio button clicked")
        content = AudioContent()
        popup = Popup(title=_("Audio"), content=content, size_hint=(0.9, 0.9), auto_dismiss=False)
        content.ids.close_button.bind(on_press=popup.dismiss)
        popup.open()


    def on_reset_button_clicked(self):
        self.logger.info("Reset button clicked")
        self.ids.bt_devices.clear_widgets()
        self.bt_adapter.reset_adapter()
        del self.bt_adapter
        self.bt_adapter = BTadapter(observer=self.observer)
        self.on_scan_button_clicked()


if __name__ == "__main__":
    from kivy.app import App

    class MainApp(App):
        def build(self):
            return Main()

    MainApp().run()



