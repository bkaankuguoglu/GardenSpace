import requests
from datetime import datetime

class GardenSpaceClient(object):


    def __init__(self, host, port, device_id):
        self.host = host
        self.port = port
        self.device_id = device_id
        self.register_path = '/api/device/register'
        self.data_path = '/api/device/data'
        self.unsynced_data = []

    def register_device(self):
        data = {}
        data['device_id'] = self.device_id

        url = 'http://{0}:{1}{2}'.format(self.host, self.port, self.register_path)
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        print url
        try:
            resp = requests.post(url, json=data, headers=headers)
            resp.raise_for_status()
        except Exception as e:
            print e
            return False
        else:
            return True

    def send_data(self, stream, value, timestamp=None):
        data = {}
        data['device_id'] = self.device_id
        data['stream_name'] = stream
        data['value'] = value
        if not timestamp is None:
            data['timestamp'] = timestamp
        else:
            data['timestamp'] = None


        url = 'http://{0}:{1}{2}'.format(self.host, self.port, self.data_path)
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        try:
            resp = requests.post(url, json=data, headers=headers)
            resp.raise_for_status()
        except Exception as e:
            print e
            self.unsynced_data.append((stream, value, timestamp))
            return False
        else:
            return True

    def send_unsynced_data(self):

        updated_unsynced_data = []

        for data in self.unsynced_data:
            result = self.send_data(data[0], data[1], data[2])
            if not result:
                updated_unsynced_data.append(data)

        self.unsynced_data = updated_unsynced_data
