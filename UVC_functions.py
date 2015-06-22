#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""Functions to access various controls on UVC-compatible cameras

Needs libwebcam and its command-line utility uvcdynctrl installed -
sudo apt-get install libwebcam

"""
import shlex, string, subprocess

def device_name():
	uvc_stdout = ""
	cmd = 'uvcdynctrl -l'
	args = shlex.split(cmd)
	try:
		uvc_stdout = subprocess.check_output(args)
	except subprocess.CalledProcessError:
		print "If using a UVC-compatible camera, please install uvcdynctrl (sudo apt-get install libwebcam) to allow manual control of focus"
		return ""
	pos = string.find(uvc_stdout, "video")
	if pos == -1:
		return ""
	else:
		devname = uvc_stdout[pos:pos+8].split()[0] # only interested in "video***" bit of the stdout
#		print "UVC_dev_name() returning", devname
		return devname

def get_focus():
	devname = device_name()
	if devname == "":
		return
	uvc_stdout = ""
	cmd = "uvcdynctrl -d " + devname + " -g 'Focus (absolute)'"
#	print("UVC_get_focus command:", cmd)
	args = shlex.split(cmd)
	uvc_result = subprocess.call(args)
	if uvc_result == 0: # command worked OK
		uvc_stdout = subprocess.check_output(args)
		try:
			return int(uvc_stdout)
		except ValueError:
			return 0
	return 0

def set_focus(focusval):
	devname = device_name()
	if devname == "":
		return
	cmd = "uvcdynctrl -d " + devname + " -s 'Focus (absolute)' " + str(focusval)
#	cmd = "uvcdynctrl -d " + devname + " -s 'Focus' " + str(focusval)  # Logitech Webcam Pro 9000
#	print("UVC_set_focus command:", cmd)
	args = shlex.split(cmd)
	uvc_result = subprocess.call(args)
	return uvc_result

def set_autofocus(auto_on_off):
	devname = device_name()
	if devname == "":
		return
	if auto_on_off:
		setval = 1
	else:
		setval = 0
	cmd = "uvcdynctrl -d " + devname + " -s 'Focus, Auto' " + str(setval)
#	print("UVC_set_autofocus command:", cmd)
	args = shlex.split(cmd)
	uvc_result = subprocess.call(args)
	return uvc_result

