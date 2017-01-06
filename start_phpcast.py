#!/usr/bin/env python

import time

import dothat.backlight as backlight
import dothat.lcd as lcd
import dothat.touch as touch
import requests

session = requests.Session()
lcd.set_cursor_position(0, 0)

paused = False

scrollX = 0
tick = 0


def refresh():
    global paused
    if not paused:
        getPlaying()
        getVolume()


# Get the current song that is playing.
def getPlaying():
    lcd.clear()
    playing = session.get('http://phpcast.local/api/getPlaying').json()['fileName']
    playing = playing.replace('.mp3', '')
    dots = '.' * 3
    playing = playing[0:12] + dots

    if playing != '':
        lcd.write(playing)
    else:
        lcd.write('No song is playing')


# Get the current volume.
def getVolume():
    lcd.set_cursor_position(0, 1)
    volume = session.get('http://phpcast.local/api/getVolume').json()
    lcd.write('Volume : ' + str(volume))
    return volume


# Add 10 to the volume.
def volumeUp():
    volume = getVolume()
    if volume <= 100:
        volume += 10
        session.post('http://phpcast.local/api/setVolume', data={
            'volume': volume
        })


# Minus 10 from the volume.
def volumeDown():
    volume = getVolume()
    if volume >= 0:
        volume -= 10
        session.post('http://phpcast.local/api/setVolume', data={
            'volume': volume
        })


def pausePlayback():
    global paused
    paused = not paused
    session.get('http://phpcast.local/api/pauseFile')
    if paused:
        lcd.clear()
        lcd.write('Paused')
    else:
        refresh()


@touch.on(touch.UP)
def handle_up(ch, evt):
    volumeUp()
    refresh()


@touch.on(touch.DOWN)
def handle_down(ch, evt):
    volumeDown()
    refresh()


@touch.on(touch.BUTTON)
def handle_button(ch, evt):
    pausePlayback()


refresh()

# Loop refresh and update the displays backlight.
while True:
    scrollX += 1
    tick += 0.01

    if tick > 100:
        refresh()
        tick = 0;

    backlight.sweep((scrollX % 360) / 360.0)
    backlight.set_graph(0)
    time.sleep(0.01)
