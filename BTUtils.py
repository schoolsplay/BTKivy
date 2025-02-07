import pprint
import subprocess

if __name__ == '__main__':
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()

import logging
import time

module_logger = logging.getLogger("bt.BTUtils")

import pydbus
from gi.repository import GLib


def unblock_bt_device(adapter):
    try:
        # List all devices managed by rfkill
        result = subprocess.run(['rfkill', 'list'], capture_output=True, text=True, check=True)
        output = result.stdout

        # Find the ID for the Bluetooth device hci0
        lines = output.split('\n')
        bt_id = None
        for line in lines:
            if 'hci0' in line:
                bt_id = line.split(':')[0]
                break

        if bt_id is None:
            module_logger.error("Bluetooth device hci0 not found.")
            return

        # Unblock the Bluetooth device hci0
        subprocess.run(['rfkill', 'unblock', bt_id], check=True)
        module_logger.debug(f"Bluetooth device hci0 (ID: {bt_id}) unblocked successfully.")

        # Retry mechanism to handle the adapter being busy
        retries = 5
        for i in range(retries):
            try:
                # Attempt to power on the adapter
                adapter.Powered = True
                module_logger.debug("Bluetooth adapter powered on successfully.")
                break
            except GLib.Error as e:
                if 'org.bluez.Error.Busy' in str(e):
                    module_logger.info(f"Adapter is busy, retrying in 2 seconds... ({i + 1}/{retries})")
                    time.sleep(2)
                else:
                    raise e
        else:
            module_logger.warning("Failed to power on the Bluetooth adapter after multiple attempts.")
    except subprocess.CalledProcessError as e:
        module_logger.error(f"Failed to unblock Bluetooth device hci0: {e}")



class Device:
    """Class representing a Bluetooth device.
    This class is a wrapper around the pydbus object representing a Bluetooth device.
    The device object is created by the BTadapter class when a new device is added to the system.
    You can get attributes of the device by using the __getitem__ method.
    for example:
    device = Device(device_path)
    print(device['Alias'])
    The following attributes are available:
    ['Adapter', 'Address', 'AddressType', 'Alias', 'Appearance', 'Blocked', 'CancelPairing', 'Class', 'Connect',
    'ConnectProfile', 'Connected', 'Disconnect', 'DisconnectProfile', 'Get', 'GetAll', 'Icon', 'Introspect',
    'LegacyPairing', 'ManufacturerData', 'Modalias', 'Name', 'Pair', 'Paired', 'PropertiesChanged', 'RSSI',
    'ServiceData', 'ServicesResolved', 'Set', 'Trusted', 'TxPower', 'UUIDs', 'WakeAllowed']"""

    def __init__(self, device, device_path):
        self.logger = logging.getLogger("bt.Device")
        self.device = device
        self.device_path = device_path
        self.logger.info(f"Im alive! {self.device!r} with path: {self.device_path}")
        #print(dir(self.device))
        self.Alias = self.device.Alias


    @property
    def paired(self) -> bool:
        return self.device.Paired

    @property
    def connected(self) -> bool:
        return self.device.Connected

    def connect(self) -> None:
        self.device.Connect(timeout=5)

    def disconnect(self) -> None:
        self.device.Disconnect(timeout=5)


class BTadapter:
    """Class containing list of adapters with peripherals and stuff to handle them
    @observer: object that implements the on_device_added method or None"""

    def __init__(self, observer=None):
        self.logger = logging.getLogger("bt.BTadapter")
        self.observer = observer
        self.adapter = None

        self.sys_bus = pydbus.SystemBus()
        self.sys_bus.subscribe(iface="org.freedesktop.DBus.ObjectManager", signal="InterfacesAdded",
                      signal_fired=self._add_device)
        self.manager = self.sys_bus.get("org.bluez", "/")
        adapter_path = "/org/bluez/hci0"
        adapter = self.sys_bus.get("org.bluez", adapter_path)
        self.adapter = adapter

        # unblock the bluetooth device, just to be sure
        unblock_bt_device(self.adapter)

    def reset_adapter(self):
        self.logger.info("Resetting adapter")
        self.sys_bus.Unsubscribe()
        try:
            # Reset the Bluetooth adapter
            subprocess.run(['sudo', 'hciconfig', 'hci0', 'reset'], check=True)
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Failed to reset Bluetooth adapter: {e}")
        else:
            self.logger.info("Bluetooth adapter reset successfully.")


    def _check_valid_device(self, device, device_path):
        if 'org.bluez.Device1' in device:
            device_parms = device['org.bluez.Device1']
            if device_parms['Alias'].count('-') >= 4:
                self.logger.info(f"Device {device_parms['Alias']} is not probably a peripheral we connect too")
                return False
            else:
                device = self.sys_bus.get("org.bluez", device_path)
                if device:
                    self.logger.info(f"Device {device_path} is valid")
                    return device
                else:
                    self.logger.info(f"Device {device_path} is not valid")
                    return False
        self.logger.info(f"Not found org.bluez.Device1 in device {device_path}")
        return False

    def _add_device(self, sender, object, iface, signal, parms, *args) -> None:
        """Callback for when a device is added"""
        if len(parms) < 2:
            self.logger.warning(f"Invalid parameters: {parms}")
            return
        if 'org.bluez.Device1' not in parms[1]:
            self.logger.warning(f"Device added without org.bluez.Device1: {parms}, skipping")
            return

        device_path = parms[0]
        device_parms = parms[1]['org.bluez.Device1']
        #pprint.pprint(device_parms)
        self.logger.info(f"Device added: {parms[0]} with alias: {device_parms['Alias']}")
        if self.observer:
            device = self.get_device(device_path)
            if device:
                self.observer.on_device_added(device)

    def get_adapter(self):
        return self.adapter

    def get_all_devices(self) -> dict:
        devices = {}
        for path, device in self.manager.GetManagedObjects().items():
            device = self._check_valid_device(device, path)
            if device:
                devices[path] = Device(device, path)
        return devices

    def get_device(self, device_path) -> Device:
        for path, device in self.manager.GetManagedObjects().items():
            if path == device_path:
                device = self._check_valid_device(device, path)
                if device:
                    return Device(device, device_path)

    def scan_adapter(self, scan_duration=5) -> None:
        self.logger.info(f"Start scanning adapter: {self.adapter}")
        if not self.adapter.Powered:
            self.adapter.Powered = True
        mainloop = GLib.MainLoop()
        GLib.timeout_add_seconds(scan_duration, mainloop.quit)
        self.adapter.StartDiscovery()
        mainloop.run()
        self.adapter.StopDiscovery()
        self.logger.info("Scan completed")

    def remove_device(self, device_path) -> None:
        self.logger.info(f"Removing device: {device_path}")
        device = self.get_device(device_path)
        #device.unpair()
        device.disconnect()

    # Doesn't seem to be implemented in pydbus/bluez
    # def pair_device(self, device) -> None:
    #     path = device.get_path()
    #     self.logger.info(f"Pairing device: {path}")
    #     self.manager.PairDevice(path)
    #
    # def un_pair_device(self, device) -> None:
    #     path = device.get_path()
    #     self.logger.info(f"Unpairing device: {path}")
    #     self.manager.UnpairDevice(path)


    def get_paired_devices(self) -> list:
        paired_devices = []
        for path, device in self.manager.GetManagedObjects().items():
            if 'org.bluez.Device1' in device:
                if device['org.bluez.Device1']['Paired']:
                    paired_devices.append(path)
        return paired_devices

    def get_connected_devices(self) -> list:
        connected_devices = []
        for path, device in self.manager.GetManagedObjects().items():
            if 'org.bluez.Device1' in device:
                if device['org.bluez.Device1']['Connected']:
                    connected_devices.append(path)
        return connected_devices

if __name__ == '__main__':

    bt_adapter = BTadapter()
    devices = bt_adapter.get_all_devices()
    print("All devices pre scan")
    for path, device in devices.items():
        print(f"Device: {path} {device.Alias}")

    print("scanning")
    bt_adapter.scan_adapter()
    devices = bt_adapter.get_all_devices()
    for path, device in devices.items():
        print(f"Device: {path} {device.Alias}")
        print(dir(device))
    print(f"connected: {bt_adapter.get_connected_devices()}")
    print(f"paired: {bt_adapter.get_paired_devices()}")





