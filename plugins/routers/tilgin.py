from bs4 import BeautifulSoup
import requests


def get_name():
    return 'Tilgin router'


def get_default_settings():
    return {'login_user': '', 'login_password': ''}


def get_available_commands():
    return {}


def get_available_queries():
    return {'active_devices': {}, 'ip_for_mac': {}}


def create(settings):
    return TilginRouter(settings)


class TilginRouter:
    def __init__(self, settings):
        self.settings = settings

        payload = {'__formtok': '', '__user': settings['login_user'], '__auth': 'login',
                   '__pass': settings['login_password']}
        url = 'http://192.168.1.1/'

        response = requests.post(url, data=payload)

        self.cookies = response.cookies

    def active_devices(self):
        response = requests.get('http://192.168.1.1/status/lan_clients/', cookies=self.cookies)

        soup = BeautifulSoup(response.text, 'lxml')

        clients_box = soup.find(id="content")

        result = []

        for table in clients_box.find_all('tbody'):
            for row in table.find_all('tr'):
                columns = row.find_all('td')
                result.append({'name': columns[0].text, 'mac': columns[1].text, 'ip': columns[2].text,
                               'type': columns[3].text, 'media': columns[4].text})

        return result

    def ip_for_mac(self, mac_address):
        devices = self.active_devices()

        items = [item for item in devices if 'mac' in item and item['mac'] == mac_address]

        return items[0]['ip']
