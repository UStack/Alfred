from xml.etree import ElementTree

import requests

from plugins.plugin_base import PluginBase


def get_available_settings():
    return ['ip_address']


def get_type():
    return VieraTv


class VieraTv(PluginBase):
    def __init__(self, plugin_id, settings_manager):
        super().__init__(plugin_id, settings_manager, default_state={'current_states': {'power': False, 'volume': 0}})

    def _send_request(self, command):
        body = (
            "<?xml version='1.0' encoding='utf-8'?> \
               <s:Envelope xmlns:s='http://schemas.xmlsoap.org/soap/envelope/' \
               s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/'> \
                <s:Body> \
                 <u:X_SendKey xmlns:u='urn:panasonic-com:service:p00NetworkControl:1'> \
                  <X_KeyEvent>" + command + "</X_KeyEvent> \
                 </u:X_SendKey> \
                </s:Body> \
               </s:Envelope>"
        )

        headers = {
            'Content-Length': str(len(body)),
            'Content-Type': 'text/xml; charset="utf-8"',
            'SOAPACTION': '"urn:panasonic-com:service:p00NetworkControl:1#X_SendKey"'
        }

        ip = self._get_setting('ip_address')

        requests.post('http://%s:55000/nrc/control_0' % ip, data=body, headers=headers)

    def _get_response(self, query):
        body = (
            "<?xml version='1.0' encoding='utf-8'?> \
               <s:Envelope xmlns:s='http://schemas.xmlsoap.org/soap/envelope/' \
               s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/'> \
                <s:Body> \
                 <u:" + query + " xmlns:u='schemas-upnp-org:service:RenderingControl:1'> \
                  <InstanceID>0</InstanceID><Channel>Master</Channel> \
                 </u:" + query + "> \
                </s:Body> \
               </s:Envelope>"
        )

        headers = {
            'Content-Length': str(len(body)),
            'Content-Type': 'text/xml; charset="utf-8"',
            'SOAPACTION': '"urn:schemas-upnp-org:service:RenderingControl:1#%s"' % query
        }

        ip = self._get_setting('ip_address')

        return requests.post('http://%s:55000/dmr/control_0' % ip, data=body, headers=headers)

    def toggle_power(self):
        self._send_request('NRC_POWER-ONOFF')

    def power_on(self):
        if not self.get_power_status():
            self.toggle_power()

            self._apply('tv_turned_on', {})

    def power_off(self):
        if self.get_power_status():
            self.toggle_power()

            self._apply('tv_turned_off', {})

    def switch_hdmi_input_to(self, hdmi):
        self._send_request('NRC_HDMI%s-ONOFF' % hdmi)

    def volume_up(self):
        self._send_request('NRC_VOLUP-ONOFF')

    def volume_down(self):
        self._send_request('NRC_VOLDOWN-ONOFF')

    def mute(self):
        self._send_request('NRC_MUTE-ONOFF')

    def get_volume(self):
        try:
            response = self._get_response('GetVolume')

            response.raise_for_status()

            root = ElementTree.fromstring(response.content)

            return root.find('.//CurrentVolume').text
        except:
            return ''

    def get_power_status(self):
        try:
            response = self._get_response('GetVolume')

            response.raise_for_status()

            return True
        except:
            return False

    def update_state(self):
        active_states = {'power': self.get_power_status(), 'volume': self.get_volume()}

        if active_states['power'] != self._state['current_states']['power']:
            if active_states['power']:
                self._apply('tv_turned_on', {})
            else:
                self._apply('tv_turned_off', {})

        if active_states['volume'] != self._state['current_states']['volume']:
            if active_states['volume']:
                self._apply('tv_volume_changed', {'new_volume': active_states['volume']})

    def get_automations(self):
        return [{
            'definition': {'initial_step': {
                'id': 'update_vieria_tv_state_for_%s' % self._get_setting('ip_address'),
                'type': '.workflows.steps.execute_plugin_command',
                'plugin_id': self._plugin_id,
                'command': 'update_state',
                'parameters': {}
            }},
            'triggers': [{'type': '.workflows.triggers.interval_trigger', 'interval': 10}]
        }]

    def _on_tv_turned_on(self, event_data):
        self._state['current_states']['power'] = True

    def _on_tv_turned_off(self, event_data):
        self._state['current_states']['power'] = False

    def _on_tv_volume_changed(self, event_data):
        self._state['current_states']['volume'] = event_data['new_volume']
