# !/usr/bin/env python
# coding: utf-8
# --------------------
# https://github.com/jazmy/raspberrypi-skinnypi
# Licensed under the GNU General Public License v3.0
# Author: Jasmine Robinson (jazmy.com)
# Last Updated: 1/27/2019
# skinnypi.py
# This Python script was created to run on a Raspberry Pi
# It listens for an MQTT message in json then parses the
# json into commands for Blinkt LED lights & audio
# ----------------------
import colorsys
import json
import threading
import time
import os

import math
import paho.mqtt.client as mqtt

import blinkt
try:
    import numpy as np
except ImportError:
    exit("This script requires the numpy module\nInstall with: sudo pip install numpy")

spacing = 360.0 / 16.0
hue = 0

color_settings = {
    '1': (167, 0, 0),  # red
    '2': (12, 0, 167),  # blue
    '3': (39, 167, 0),  # green
}

style_settings = {
    '1': 'rainbow',
    '2': 'gradient',
    '3': 'flow'
}

#Your MQTT Server Settings
MQTT_SERVER = "Your Server"
MQTT_PORT = 17540
MQTT_TOPIC = "Your Topic"
# Set these to use authorization
MQTT_USER = "Your Username"
MQTT_PASS = "Your Password"


def Play_sound(start_time, duration_time, filename):
    os.system('aplay -d {} {}'.format(duration_time, filename))

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print('Message have received')
    # Example json data: { "color": "1", "style": "1", "seconds": "10", "audio": "1"}
    # Color = (1=red,2=blue,3=green)
    # Style = (1=rainbow,2=gradient,3=flow)
    # Audio = (1 = 1.wav,2 = 2.wav)
    # Seconds = how many seconds should it play
    data = msg.payload.decode()
    data = json.loads(data)
    print(data)

    try:
        audio_filename = '/home/pi/skinnypi/{}.wav'.format(data['audio'])  # You may need to update the path
        audio_playing_time = int(data['seconds'])
        start_time = time.time()
        thread = threading.Thread(target=Play_sound, args=(start_time, audio_playing_time, audio_filename))
        thread.start()
    except Exception as e:
        print(e)

    #  Color should control the color of the lights. Unless it’s rainbow because that is all the colors.
    color = color_settings[data['color']]

    # style - values(rainbow, gradient, flow)
    style = style_settings[data['style']]

    # To avoid default brightness from previous call
    blinkt.set_brightness(0.2)

    if style == 'rainbow':
        spacing = 360.0 / 16.0

        while True:
            end_time = time.time()
            if end_time > start_time + audio_playing_time:
                blinkt.set_all(0, 0, 0, )
                blinkt.show()
                print('ready for new message')
                return None
            hue = int(time.time() * 100) % 360
            pixels = blinkt.NUM_PIXELS
            for x in range(pixels):
                offset = x * spacing
                h = ((hue + offset) % 360) / 360.0
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
                blinkt.set_pixel(x, r, g, b)

            blinkt.show()
            time.sleep(0.001)

    elif style == 'gradient':
        hue_range = 120
        hue_start = 0
        max_brightness = 0.2

        def show_graph(v, r, g, b):
            v *= blinkt.NUM_PIXELS
            for x in range(blinkt.NUM_PIXELS):
                hue = ((hue_start + ((x / float(blinkt.NUM_PIXELS)) * hue_range)) % 360) / 360.0
                r, g, b = color
                if v < 0:
                    brightness = 0
                else:
                    brightness = min(v, 1.0) * max_brightness
                blinkt.set_pixel(x, r, g, b, brightness)
                v -= 1
            blinkt.show()
        blinkt.set_brightness(0.1)
        try:
            while True:
                end_time = time.time()
                if end_time > start_time + audio_playing_time:
                    blinkt.set_all(0, 0, 0, )
                    blinkt.show()
                    print('ready for new message')
                    return None
                t = time.time() * 2
                v = (math.sin(t) + 1) / 2  # Get a value between 0 and 1
                show_graph(v, 255, 0, 255)
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass

    elif style == 'flow':

        REDS = [0, 0, 0, 0, 0, 16, 64, 255, 64, 16, 0, 0, 0, 0, 0, 0]

        flow_start_time = time.time()

        while True:
            end_time = time.time()
            if end_time > start_time + audio_playing_time:
                blinkt.set_all(0, 0, 0, )
                blinkt.show()
                print('ready for new message')
                return None

            # Triangle wave, a snappy ping-pong effect
            delta = (time.time() - flow_start_time) * 16
            offset = int(abs((delta % len(REDS)) - blinkt.NUM_PIXELS))

            for i in range(blinkt.NUM_PIXELS):
                if color == (167, 0, 0): # red
                    blinkt.set_pixel(i, REDS[offset + i], 0, 0)
                elif color == (39, 167, 0): # green
                    blinkt.set_pixel(i, 0, REDS[offset + i], 0)
                elif color == (12, 0, 167): # blue
                    blinkt.set_pixel(i, 0, 0,  REDS[offset + i])
                else:
                    blinkt.set_pixel(i, REDS[offset + i], 0, 0) # by default red

            blinkt.show()

            time.sleep(0.1)
    return None


def main():
    blinkt.set_clear_on_exit()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    if MQTT_USER is not None and MQTT_PASS is not None:
        print("Using username: {un} and password: {pw}".format(un=MQTT_USER, pw="*" * len(MQTT_PASS)))
        client.username_pw_set(username=MQTT_USER, password=MQTT_PASS)

    client.connect(MQTT_SERVER, MQTT_PORT, 60)

    client.loop_forever()


if __name__ == '__main__':
    main()
