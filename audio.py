import logging
import pulsectl

class PulseInfo:
    """PulseAudio information"""
    def __init__(self, domain='btkivy'):
        # sink_hash is a dictionary with the following structure:
        # {description: {sink_name: string, volume: float, state: Boolean}}
        self.sink_hash = {}
        self.default_sink = {}
        self.domain = domain
        self.logger = logging.getLogger('bt.PulseInfo')


    def get_sinks(self) -> dict:
        self.logger.info("get_sinks")

        with pulsectl.Pulse(self.domain) as pulse:
            try:
                for sink in pulse.sink_list():
                    self.sink_hash[sink.description] = {'sink_name': sink.name, 'volume': sink.volume.value_flat,
                                                        'state': sink.state._value == 'running'}
            except Exception as e:
                self.logger.error("Error getting PulseAudio sinks", exc_info=True)
                self.sink_hash = {'default': {'sink_name': 'No sinks found', 'volume': 0.85, 'state': False}}
            else:
                self.logger.info(f"found sinks: {self.sink_hash!r}")
            return self.sink_hash

    def get_default_sink(self) -> dict:
        self.logger.info("get_default_sink")
        with pulsectl.Pulse(self.domain) as pulse:
            try:
                sink = pulse.sink_default_get()
            except Exception as e:
                self.logger.error("Error getting PulseAudio default sink", exc_info=True)
                return {'default': {'sink_name': 'No sinks found', 'volume': 0.85, 'state': False}}
            else:
                self.logger.info(f"found default sink: {sink!r}")
                self.default_sink[sink.description] = {'sink_name': sink.name, 'volume': sink.volume.value_flat,
                                                    'state': sink.state._value == 'running'}
                return self.default_sink

    def set_default_sink(self, sink_name) -> bool:
        self.logger.info(f"set_default_sink: {sink_name}")
        with pulsectl.Pulse(self.domain) as pulse:
            try:
                for sink in pulse.sink_list():
                    if sink.name == sink_name:
                        pulse.sink_default_set(sink)
                        break
            except Exception as e:
                self.logger.error("Error setting PulseAudio default sink", exc_info=True)
                return False
            else:
                return True

    def set_sink_volume(self, sink_name='', volume=0.85) -> bool:
        self.logger.info(f"set_sink_volume: {sink_name} {volume}")
        if not sink_name:
            sink_name = self.get_default_sink()
            self.logger.info(f"set_sink_volume: default sink {sink_name}")
        with pulsectl.Pulse(self.domain) as pulse:
            try:
                for sink in pulse.sink_list():
                    if sink.name == sink_name:
                        pulse.volume_set_all_chans(sink, volume)
                        break
            except Exception as e:
                self.logger.error("Error setting PulseAudio sink volume", exc_info=True)
                return False
            else:
                return True

if __name__ == '__main__':
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
    pi = PulseInfo()
    sinks = pi.get_sinks()
    print(f"sinks: {sinks}")
    default_sink = pi.get_default_sink()
    print(f"default_sink: {default_sink!r}")
    # pi.set_default_sink('alsa_output.pci-0000_00_1f.3.analog-stereo')
    # pi.set_sink_volume('alsa_output.pci-0000_00_1f.3.analog-stereo', 0.5)
    # pi.set_sink_volume(volume=0.5)
    # pi.get_sinks()
    # pi.get_default_sink()