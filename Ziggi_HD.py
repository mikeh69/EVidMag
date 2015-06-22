#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""Functions to access the USB HID component of the Ipevo Ziggi HD document camera

Needs HIDAPI and its Python bindings installed -
sudo apt-get install hidapi, then
pip2 install hidapi

"""
import hid
import time

initialised = False

def initialise():
    # trigger_autofocus doesn't always work from a reboot with the camera plugged in
    # work out what to send to initialise it...
    initialised = True
    return 0

def trigger_autofocus():
    if not initialised:
        initialise()
    try:
#        print "Opening device"
        h = hid.device()
        h.open(0x1778, 0x0210) # Ipevo Ziggi HD document camera
#        print "Manufacturer: %s" % h.get_manufacturer_string()
#        print "Product: %s" % h.get_product_string()
#        print "Serial No: %s" % h.get_serial_number_string()
        # try non-blocking mode by uncommenting the next line
        #h.set_nonblocking(1)
        h.write([0x02, 0x4F, 0x00, 0x00, 0x00]) # the magic numbers to trigger an auto-focus
        time.sleep(0.05)
#        print "Closing device"
        h.close()

    except IOError, ex:
        print ex
#    print "Done"
    return 0

if __name__ == "__main__":
    trigger_autofocus()
