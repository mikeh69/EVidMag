# EVidMag

EVidMag - a Free Open-Source Video Magnifier for people with impaired vision
===========================================================================

Introduction
------------

An Electronic Video Magnifier shows an image of a hard-copy document on an 
LCD screen, and allows the user to zoom in and out, enhance brightness/contrast,
invert light/dark and generally make the content more visible to someone with
impaired vision.  A number of companies sell purpose-made EVMs, both handheld
devices and desktop systems, but they are quite expensive ($2k up for desktop).

This project aims to use an inexpensive USB high-definition document camera 
(or even a cheap webcam!) linked to a PC to provide the image-manipulation 
functions of a desktop EVM system at much lower cost.  The hardware aspects 
(e.g. mounting the camera looking downwards onto a convenient flat surface) 
are up to you! Commercial desktop EVMs also provide a rolling "platen" to 
allow a book or document to be moved around smoothly below the camera.


Camera
------

The preferred camera for this project is the Ipevo Ziggi HD, a USB document
camera with up to 5Mpixel resolution and costing around £80 UK / 100USD.
Other UVC-compliant cameras will work to some degree, but may give poorer
results and/or prevent some features from working.


Versions
--------

The initial version (started May 2015) of VidMag uses version 2.4 of the OpenCV
library and version 2.7 of Python (the default versions of these packages for
Ubuntu 14.04).  In time, it will probably migrate to version 3.0 of OpenCV, 
allowing it to move over to Python 3.  OpenCV 3 also provides text-recognition 
functions, which might allow clean re-rendering of poorly-printed text.

Initial development is on a Linux platform, with a medium-term goal of creating
a stand-alone system based on a Raspberry Pi.  The main part of the software 
should work perfectly well on Windows, as long as the camera's built-in 
auto-focus performs adequately when viewing text documents at short range.


Dependencies
------------

VidMag depends on the following external packages:

- OpenCV - open-source computer-vision library
- OpenCV-Python - Python bindings for OpenCV
- v4l2-utils - to set camera frame-size and format
- libwebcam - for manual control of camera focussing
- hidapi-python, hidapi, cython - to trigger auto-focus on Ipevo Ziggi-HD camera


Building
--------

No compilation or building is required, unless there is no pre-built version
of libwebcam available for your flavour of Linux.  The VidMag software is 
written entirely in Python script, so just needs a Python interpreter installed.


Installation
------------

!Not yet complete!
<TBA>

sudo apt-get install libusb libhidapi-libusb0
pip2 install cython
pip2 install hidapi


Shamelessly copied and adapted from Jan Axelson's excellent USB website:
<QUOTE>
By default, applications that use the libusb-1.0 library require administrative
privileges (sudo). To enable users to access a device via the libusb-1.0 
library without administrative privileges, add a udev rule for the device. 
This rule specifies the USB device with Vendor ID = 1778h and Product ID = 0210h
(Ipevo Ziggi-HD document camera) and sets the MODE parameter to grant read/write
permissions for all users:

SUBSYSTEM=="usb", ATTR{idVendor}=="1778", ATTR{idProduct}=="0210", MODE="0666"

The rule should be on one line in the file. (Press Enter only at the end.) 
Place the rule in a file with a .rules extension (such as 81-libusb.rules) 
and save the file in /etc/udev/rules.d/  On the next device attachment or boot, 
users can run applications that use libusb-1.0 functions to read and write to 
the specified device.
</QUOTE>


Compatible devices
------------------

Cameras tested so far are:

- Ipevo Ziggi-HD document camera (ID 1778:0210) - 4 x 3 aspect-ratio 5Mpixel (2592 x 1944)
- Logitech C920 (ID 046d:082d) - 16 x 9 aspect-ratio 2Mpixel (1920 x 1080).
- Logitech Webcam Pro 9000 for Business (ID 046d:0809) - 4 x 3 aspect-ratio 2Mpixel (1600 x 1200).

Note: the "ID" can be found by using the command "lsusb".

The C920 auto-focus is not reliable, which drove the inclusion of manual-
focus functions in VidMag.

Before trying out VidMag, it's worth checking that your camera is basically 
working using guvcview:
  sudo apt-get install guvcview
  guvcview
If it doesn't work, try unplugging the camera from USB, wait a few seconds, then
plug it in again and retry.  Still looking for a solution to this issue with
Logitech C920 on Ubuntu 14.04!


Questions and feedback
----------------------

Please email me with expressions of interest, bug reports, suggestions:
  mikeh_opensource (at) btinternet.com


