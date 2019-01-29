# SkinnyPi - Weight Loss Party - Python Script

A [Laravel](https://laravel.com), [Raspberry Pi](https://www.raspberrypi.org/) & [FitBit](https://www.fitbit.com) Project for Weight Loss Party Mode

I thought it would be fun to setup a Raspberry Pi so that every time I lost weight, it would flash lights and play music. I referred to this as “Party mode” or “Happy Dance.” It would be positive reinforcement and a fun way to start my morning. I had just completed an “Internet of Things” MIT course in Grad School so I had a basic understanding of communication protocols.

This is the Python Blinkt Script for listening for MQTT messages, in json format, and parsing them to control the Blinkt LED lights and audio.

**For the complete project go to -  https://github.com/jazmy/laravel-skinnypi**

## Setup your Python Scripts to Run Automatically on Boot

https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup#method-1-rclocal

```unix  
sudo nano /etc/rc.local
```

This is tricky but you need to ensure that you wait 10 seconds to give your pi enough time to boot and connect to the network before you run your script. This will create a log file if there are problems.

```unix  
sudo bash -c '(sleep 10;/usr/bin/python3 /home/pi/skinnypi/skinnypi.py > /home/pi/skinnypi/skinnypi.log 2>&1)' &
```

## Example JSON

 **Color** *(color of the lights)*  1=red, 2=blue, 3=green
 
 **Style** *(animation of the lights)* 1=rainbow, 2=gradient, 3=flow
 
 **Audio** *(filename of the .wav to play)*  1 = 1.wav, 2 = 2.wav
 
 **Seconds** *(how many seconds should it play)*  5, 10, 20

If the user has lost weight it should send this json to MQTT:

```json
$message = { "color": "1", "style": "1", "seconds": "10", "audio": "1"}
```

If the user has not lost weight it should send this json to MQTT:

```json
$message = { "color": "2", "style": "2", "seconds": "10", "audio": "2"}
```
