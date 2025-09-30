# ARTNET-TO-USBDMX
This Python program allows you to use the Digital Enlightenment FX5-USBDMX interface as an Art-Net node.

Requirements:

A Linux-based system (e.g., Raspberry Pi) to run the script

The Digital Enlightenment FX5-USBDMX interface (other devices are not supported)

An external power supply for the interface if your machine’s USB ports do not provide sufficient power
(recommended: 9–12 V PSU)

Notes:

The script generally works without installing additional dependencies.

If you encounter issues, you may need to adjust the path to the usbdmx.so library.

How it Works:

When the interface is connected and the script is started, the device is automatically detected and switched into Mode 6:

PC Out → DMX Out

DMX In → PC In

Additionally, parameters such as operating mode or the Art-Net universe can be customized directly within the source code.
