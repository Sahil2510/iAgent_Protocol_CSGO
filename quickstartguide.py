import os
import time
import mss
import cv2
import socket
import sys
import struct
import math
import random
import win32api as wapi
import win32api
import win32gui
import win32process
import ctypes
from ctypes  import *
from pymem   import *

import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

import numpy as np
import matplotlib.pyplot as plt

from key_input import key_check, mouse_check, mouse_l_click_check, mouse_r_click_check
from key_output import set_pos, HoldKey, ReleaseKey
from key_output import left_click, hold_left_click, release_left_click
from key_output import w_char, s_char, a_char, d_char, n_char, q_char
from key_output import ctrl_char, shift_char, space_char
from key_output import r_char, one_char, two_char, three_char, four_char, five_char
from key_output import p_char, e_char, c_char_, t_char, cons_char, ret_char

from screen_input import grab_window
from config import *
from meta_utils import *


class MyServer(HTTPServer):
    def __init__(self, server_address, token, RequestHandler):
        self.auth_token = token
        self.round_phase = None
        self.training_data = []

        super(MyServer, self).__init__(server_address, RequestHandler)


class MyRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server, hwin_csgo):
        self.hwin_csgo = hwin_csgo
        self.csgo_game_res = (1024, 768)  # Replace with your actual game resolution
        self.data_all = {}
        super(MyRequestHandler, self).__init__(request, client_address, server)

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode('utf-8')

        self.parse_payload(json.loads(body))

        self.send_header('Content-type', 'text/html')
        self.send_response(200)
        self.end_headers()

    def is_payload_authentic(self, payload):
        if 'auth' in payload and 'token' in payload['auth']:
            return payload['auth']['token'] == server.auth_token
        else:
            return False

    def parse_payload(self, payload):
        # Ignore unauthenticated payloads
        if not self.is_payload_authentic(payload):
            return None

        round_phase = self.get_round_phase(payload)

        if round_phase != self.server.round_phase:
            self.server.round_phase = round_phase
            print('New round phase:', round_phase)
            self.save_data()  # Save data when round phase changes

        if 'allplayers' in payload:
            self.data_all = payload

    def get_round_phase(self, payload):
        if 'round' in payload and 'phase' in payload['round']:
            return payload['round']['phase']
        else:
            return None

    def log_message(self, format, *args):
        """
        Prevents requests from printing into the console
        """
        return

    def save_data(self):
        # Capture screenshot
        img = grab_window(self.hwin_csgo, game_resolution=self.csgo_game_res, SHOW_IMAGE=False)

        # Get GSI info
        gsi_team = None
        gsi_health = None
        gsi_kills = None
        gsi_deaths = None
        gsi_weapons = None

        if 'player' in self.data_all:
            gsi_player = self.data_all['player']
            gsi_team = gsi_player.get('team', None)
            gsi_health = gsi_player.get('state', {}).get('health', None)
            gsi_kills = gsi_player.get('match_stats', {}).get('kills', None)
            gsi_deaths = gsi_player.get('match_stats', {}).get('deaths', None)
            gsi_weapons = gsi_player.get('weapons', None)

        # Get metadata
        metadata = {
            "round_phase": self.server.round_phase,
            "gsi_team": gsi_team,
            "gsi_health": gsi_health,
            "gsi_kills": gsi_kills,
            "gsi_deaths": gsi_deaths,
            "gsi_weapons": gsi_weapons,
            # Add other metadata fields here
        }

        # Append data to training_data
        self.server.training_data.append([img, metadata])

        # Save data in .npy file if enough data is collected
        if len(self.server.training_data) >= 1000:
            file_name = 'training_data_{}.npy'.format(int(time.time()))
            np.save(file_name, self.server.training_data)
            print('SAVED', file_name)
            self.server.training_data = []


def main():
    # ... (Previous code remains unchanged)

    # Find the required process and where two modules (dll files) are in RAM
    hwin_csgo = win32gui.FindWindow(0, ('Counter-Strike: Global Offensive - Direct3D 9'))
    if hwin_csgo:
        pid = win32process.GetWindowThreadProcessId(hwin_csgo)
        handle = pymem.Pymem()
        handle.open_process_from_id(pid[1])
        csgo_entry = handle.process_base
    else:
        print('CSGO was not found')
        os.system('pause')
        sys.exit()

    # ... (Previous code remains unchanged)

    server = MyServer(('localhost', 27015), 'EB2B3DCFB1FD6564EB4AD01A003934C3', lambda request, client_address, server: MyRequestHandler(request, client_address, server, hwin_csgo))

    print(time.asctime(), '-', 'CS:GO GSI Quick Start server starting')

    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

    server.server_close()
    print(time.asctime(), '-', 'CS:GO GSI Quick Start server stopped')


if __name__ == "__main__":
    main()
