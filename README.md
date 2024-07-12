# rp2040 with esp8285, getting wifi to work

A While ago, i bought (what i tought) was a genuine raspberry pi pico w on aliexpress... I tought i was buying a genuine device from the reseller TZT. However, when trying to connect to wifi, it just didn't work... The connect function failed, in circuitpython i got the error message `[CYW43] Failed to start CYW43`.  
It took me a while to figure out TZT sells knockoff pico's, and they use a different wifi module (an esp8285).  
This means that the "default" raspberry pi pico w firmware (installed manually, or trough thonny or ....) simply does not work.  

i found some guys on [the raspberry pi forum](https://forums.raspberrypi.com/viewtopic.php?t=361532) that discussed (and solved) the problem. But still, their walktrough wasn't dummy-proof, so i decided to write down all my steps, and a demo program posting some data to ntfy.sh!!!

## step 1: flash esp8285 firmware

As a very first step, we'll need to get some firmware onto our esp8285 chip

### upload firmware to rp2040

We need to install Serial_port_transmission.uf2 (available on this repo) on rp2040. To do this, press the bootsel button closest to the usb connector and hold the button down whilst plugging in your raspberry pi. When plugged in, your OS should detect your raspberry as a removable device. Copy Serial_port_transmission.uf2 onto this removable device and wait for the file to be uploaded and the rPi to be rebooted.  

### upload firmware to esp8285

* Download the [flash download tool](https://www.espressif.com/en/support/download/other-tools) from espressif
* unplug your python, hold the "other" button down (the one furthest from the usb port) and connect your pico to your pc
* Start the flash download tool
* in the first menu, choose "chip type" esp8285
* choose file WIFI-ESP8285_upgrade.bin (available on this repo) @ 0x0
* leave all the rest (SPI speed 40 MHz, SPI mode DOUT, DoNotChgBin selected)
* make sure your COM port is correct (you can use your device manager, or thonny to find out which com port to use)
* press "Start" and wait untill finished

## step 2: flash rp2040 with micropython

* unplug your pico, hold bootsel button down, plug python in
* either use thonny to install micropython, or download and copy to your pico

## step 3: upload main.py

connect your pico, start thonny, select the board in the bottom right corner, copy my main.py file and edit the SSID and password... Then run (and check ntfy.sh if a message was posted in the channel you picked)

## debugging

If something goes wrong, you can always re-flash the rp2040 with Serial_port_transmission.uf2 and open putty. Select a serial connection, edit the COM port, change the speed to 115200 and connect. Now you can give AT command directly to the esp8285. Putty does not send \r\n by default, so you need to enter an AT command, press enter, then press CTRL-J.  
If you want to learn more about AT commands, you can visit [this](https://docs.espressif.com/projects/esp-at/en/release-v2.2.0.0_esp8266/AT_Command_Set/index.html) page.  
IF you cannot get it to work, you can always open an issue, but i'm not affiliated with espressif, tzt, raspberry,... so i'm not sure if i can help you out... Doesn't hurt to ask tough!
