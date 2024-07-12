# rp2040 with esp8285, getting wifi to work

A While ago, i bought (what i tought) was a genuine raspberry pi pico w on aliexpress... I tought i was buying a genuine device from the reseller TZT. However, when trying to connect to wifi, it just didn't work... The connect function failed, in circuitpython i got the error message `[CYW43] Failed to start CYW43`.  
It took me a while to figure out TZT sells knockoff pico's, and they use a different wifi module (an esp8285).  
This means that the "default" raspberry pi pico w firmware (installed manually, or trough thonny or ....) simply does not work.  

i found some guys on [the raspberry pi forum](https://forums.raspberrypi.com/viewtopic.php?t=361532) that discussed (and solved) the problem. But still, their walktrough wasn't dummy-proof, so i decided to write down all my steps, and a demo program posting some data to ntfy.sh!!!

Step 1:
