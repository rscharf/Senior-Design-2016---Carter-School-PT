import RPi.GPIO as GPIO
import time
import os
from subprocess import Popen
import psutil

SCRIPT_NAME = "/home/pi/newGUIwI2C/screen.py"
buttonPin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(buttonPin, GPIO.IN)
prev_input = 1

while True:
	input = GPIO.input(buttonPin)
	if ((not prev_input) and input):
		#button pressed
		#find process and kill it
		for proc in psutil.process_iter():
			if SCRIPT_NAME in proc.cmdline():
				proc.kill()

	
	prev_input = input
	time.sleep(0.05)