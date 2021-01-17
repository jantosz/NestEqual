import requests
import time
import threading
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import platform
from copy import deepcopy

import send_text

DEBUG = False

load_dotenv()
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
PROJ_ID = os.getenv('PROJECT_ID')
CP_PROJ_ID = os.getenv('CP_PROJ_ID')
access_token = 'NO ACCESS TOKEN'


# SET THIS TO FALSE IF YOU DO NOT WANT TEXT MESSAGES WHEN EXCEPTIONS OCCUR
SEND_TEXT = True

if SEND_TEXT:
    PHONE_NUM = os.getenv('PHONE_NUMBER')
    # This is added to the phone number to send an email that will be sent as a text
    PROVIDER_EMAIL = '@tmomail.net'


# SET THIS TO YOUR LOCAL TIME ZONE FOR ACCURATE LOGGING
# Will have no effect if running on Windows. Then, it will just use the system's default timezone.
TIMEZONE = 'America/Los_Angeles'


def get_access_token():
    global access_token
    url = 'https://www.googleapis.com/oauth2/v4/token?'
    req_data = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'refresh_token': REFRESH_TOKEN,
                'grant_type': 'refresh_token'}
    returned_json = json.loads(requests.post(url, data=req_data).text)
    access_token = returned_json['access_token']
    print('Generated new access token at', datetime.now().strftime('%H:%M:%S'))


def refresh_access():
    while True:
        time.sleep(3300)
        get_access_token()


def loop_device_check():
    # Every 15 seconds, if one of your thermostats has changed modes, will change the other thermostats' modes to that
    # new mode. If any thermostats are OFF or in ECO MODE, this does nothing.
    past_devices = get_devices()
    while len(past_devices) < 2:
        time.sleep(15)
        past_devices = get_devices()

    if SEND_TEXT:
        text_sent = False

    while True:
        try:
            if DEBUG:
                print('looping device check')
            devices = get_devices()
            while len(devices) < 2:
                time.sleep(15)
                devices = get_devices()
            if DEBUG:
                print('FOUND', len(devices), 'DEVICES')
                for dev_n, dev in devices.items():
                    print('DEVICE NAME:', dev_n, '\nDICT:', dev)
            for dev_name, dev in devices.items():
                if past_devices[dev_name]['marked'] or dev['traits']['sdm.devices.traits.ThermostatMode']['mode'] == \
                        'OFF' or dev['traits']['sdm.devices.traits.ThermostatEco']['mode'] != 'OFF':
                    if DEBUG:
                        print('A device is off, in eco mode, or marked.')
                    continue
                if dev['traits']['sdm.devices.traits.ThermostatMode']['mode'] != \
                        past_devices[dev_name]['traits']['sdm.devices.traits.ThermostatMode']['mode']:
                    if DEBUG:
                        print('Mode change found!')
                    for other_dev_name, other_dev in devices.items():
                        if other_dev_name == (dev_name
                                              or other_dev['traits']['sdm.devices.traits.ThermostatMode'][
                                                  'mode'] == 'OFF'
                                              or other_dev['traits']['sdm.devices.traits.ThermostatEco']['mode']
                                              != 'OFF'):
                            continue
                        if DEBUG:
                            print('Setting mode...')
                        set_mode(other_dev_name, dev['traits']['sdm.devices.traits.ThermostatMode']['mode'])
                        devices[other_dev_name]['marked'] = True

            past_devices = deepcopy(devices)
            time.sleep(15)

            if SEND_TEXT:
                text_sent = False
        except Exception as e:
            print('EXCEPTION: ' + str(e))
            if SEND_TEXT and not text_sent:
                send_text.send(PHONE_NUM, PROVIDER_EMAIL, 'EXCEPTION IN NEST_EQUAL', str(e))
                text_sent = True
                print('Text message sent!')


def get_devices():
    while True:
        try:
            url = f'https://smartdevicemanagement.googleapis.com/v1/enterprises/{PROJ_ID}/devices'
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token}
            returned_json = json.loads(requests.get(url, headers=headers).text)
            devdict = dict()
            for device in returned_json['devices']:
                if 'sdm.devices.traits.ThermostatMode' in device['traits'].keys():
                    devdict[device['name']] = device
                    devdict[device['name']]['marked'] = False
            return devdict
        except KeyError:
            print('KEY ERROR IN GET DEVICES')
            time.sleep(15)


def set_mode(device_name, mode):
    url = f'https://smartdevicemanagement.googleapis.com/v1/{device_name}:executeCommand'
    post_data = {'command': 'sdm.devices.commands.ThermostatMode.SetMode',
                 'params': {'mode': mode.upper()}}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
    req = requests.post(url, data=json.dumps(post_data), headers=headers)
    print(req.text, 'at', datetime.now().strftime('%H:%M:%S'))


if __name__ == '__main__':
    if platform.system() != 'Windows':
        os.environ['TZ'] = TIMEZONE
        time.tzset()
    get_access_token()
    threading.Thread(target=refresh_access).start()
    loop_device_check()
