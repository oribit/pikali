# pikali: Pentesting station for Rapsberry with TFT screen and Kali Linux

Initially, I thought this project as a fork from the amazing KALI-PI Launcher by Re4son (https://github.com/re4son/pitftmenu). But finally, I rebuilt it from zero, because I want to use it as a portable and autonomous pentesting device. So, I had to add new tools and a way to configure and use it in a different way.

The idea behind this project, it's to give you the possibility to perform a quick pentest "on the fly". Also, it could be use as part of a large pentesting process.

The project is far from be finished, but I think it's in a good point to start, and even more to listen any new idea or critics about it.

#Requisites
- First, a Raspberry Pi, without it... we are not starting really well.
- Also, this project will need a screen to display menus... so, better than go to the street with a portable Raspberry and a TV, could be to install a TFT Screen. There is an absolutely awesome guide from Re4son about how to do it here: https://whitedome.com.au/re4son/kali-pi/. You will not find any other place better explained.
- Finally, we will need some libraries for Python: pygame and RPi.GPIO, both can be installed easily with PIP.

#Screenshots

These are some screen captures:
Main screen
![Main screen](/screenshots/main.jpg?raw=true "Main screen")

IP Menu screen
![IP menu screen](/screenshots/ip.jpg?raw=true "IP menu screen")

Services menu
![Services menu screen](/screenshots/services.jpg?raw=true "Services menu screen")
