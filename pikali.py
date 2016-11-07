#!/usr/bin/env python
import sys, os, time, subprocess, pygame, threading
import RPi.GPIO as GPIO
import pikali_bag
from pikali_bag import *
from pygame.locals import *


# Global variables
screen_status=1 # 0 off 1 on
menu_pos = 1 # Which menu is showing
ipversion = 'IPv4'
service_matrix = {}

class dataBackground(object):
    #Calculate different data in the background and display it. The update is every 5 seconds.

    def __init__(self, interval=10):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        global screen, screen_status, menu_pos

        while True:
            if screen_status and menu_pos == 1:
                print_measure_data(screen)
            # Always sleep!
            time.sleep(self.interval)


os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
#launch_bg=os.environ["MENUDIR"] + "launch-bg.sh"
#process = subprocess.call(launch_bg, shell=True)

# Initialize pygame modules individually (to avoid ALSA errors) and hide mouse
pygame.font.init()
pygame.display.init()

pygame.mouse.set_visible(0)

# matrix (x, y, width, height, function_to_call)
matrix = []


# define function that checks for touch location. Using position matrix for that.
def on_touch():
    # get the position that was touched
    touch_pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
    sys.stderr.write(str("MOUSE X: " + str(pygame.mouse.get_pos()[0]) + " MOUSE Y: " + str(pygame.mouse.get_pos()[1]) +"\n"))
    sys.stderr.write(str(str(matrix) +"\n"))
    # matrix (x, y, width, height, function_to_call)
    for i in range(len(matrix)):
        x = matrix[i][0]
        y = matrix[i][1]
        max_x = x + matrix[i][2]
        max_y = y + matrix[i][3]
        if x <= touch_pos[0] <= max_x and y <= touch_pos[1] <= max_y:
            button(matrix[i][4])
            break


def run_cmd(cmd):
    process = Popen(cmd.split(), stdout=PIPE)
    output = process.communicate()[0]
    return output

def shutdown():
    pygame.quit()
    run_cmd("/usr/bin/sudo /sbin/shutdown -h now")
    sys.exit()

def restart():
    pygame.quit()
    run_cmd("/usr/bin/sudo /sbin/shutdown -r now")
    sys.exit()

def screen_off():
    global screen_status
    screen_status = 0
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    backlight = GPIO.PWM(18, 0.1)
    backlight.start(0)
    #process = subprocess.call("setterm -term linux -back black -fore black -clear all", shell=True)

def screen_on():
    global screen_status
    screen_status=1
    backlight = GPIO.PWM(18, 1023)
    backlight.start(100)
    GPIO.cleanup()


# Define each button press action
def button(number):
    global screen
    global matrix
    global menu_pos, ipversion, service_matrix

    sys.stderr.write("Button: " + str(number) +"\n")

    if number == '0':
        menu_pos = 2
        screen.fill(colors['black'])
        matrix = []
        matrix.append([10, 10, 80, 80, 'menu1'])
        icon = pygame.image.load("imgs/back.png")
        icon = pygame.transform.scale(icon, (80, 80))
        screen.blit(icon, [10, 10])
        matrix.append([260, 105, 210, 55, 'screenoff'])
        make_button(screen, "   Screen Off", 260, 105, 210, 55, colors['yellow'])
        matrix.append([260, 180, 210, 55, 'reboot'])
        make_button(screen, "      Reboot", 260, 180, 210, 55, colors['yellow'])
        matrix.append([260, 255, 210, 55, 'shutdown'])
        make_button(screen, "   Shutdown", 260, 255, 210, 55, colors['yellow'])

    if number == 'xwin':
        menu_pos = 2
        screen.fill(colors['black'])
        matrix = []
        matrix.append([10, 10, 80, 80, 'menu1'])
        icon = pygame.image.load("imgs/back.png")
        icon = pygame.transform.scale(icon, (80, 80))
        screen.blit(icon, [10, 10])
        matrix.append([30, 230, 210, 55, 'xtft'])
        make_button(screen, "    X on TFT", 30, 230, 210, 55, colors['yellow'])
        matrix.append([260, 230, 210, 55, 'xhdmi'])
        make_button(screen, "   X on HDMI", 260, 230, 210, 55, colors['yellow'])

    if number == 'xtft':
        # X TFT
        menu_pos = 0
        # To start XWindow, the display has to be "un-initialized", after executing this, it's not possible to recover pygame
        pygame.quit()

        # Using Popen and more important communicate, we wait for the end of startx
        cmd="/usr/bin/sudo FRAMEBUFFER=/dev/fb1 startx"
        process = Popen(cmd.split(), stdout=PIPE)
        process.communicate()[0]

        # We need to execute again the program, it's the only way to reinitialize everything
        os.execv(__file__, sys.argv)

    if number == 'xhdmi':
        # X HDMI
        menu_pos = 0
        # Read comments from X TFT
        pygame.quit()
        cmd="/usr/bin/sudo FRAMEBUFFER=/dev/fb0 startx"
        process = Popen(cmd.split(), stdout=PIPE)
        process.communicate()[0]

        os.execv(__file__, sys.argv)

    if number == 'shell':
        # exit
        pygame.quit()
        #process = subprocess.call("setterm -term linux -back default -fore white -clear all", shell=True)
        sys.exit()

    if number == 'screenoff':
        menu_pos = 0
        screen_off()

    if number == 'shutdown':
        shutdown()

    if number == 'reboot':
        restart()

    if number == 'menu1':
        menu_pos = 1
        print_menu1(screen, matrix, pi_hostname)

    if number.startswith('netinfo'):
        menu_pos = 2
        if number == 'netinfo_kismet':
            pygame.quit()
            subprocess.call("/usr/bin/kismet")
            os.execv(__file__, sys.argv)
            sys.exit()

        if number == 'netinfo_sdr':
            pygame.quit()
            cmd="/bin/bash " + os.path.dirname(os.path.abspath(__file__)) + "/sdr-scanner.sh"
            process = Popen(cmd.split(), stdout=PIPE)
            process.communicate()[0]
            os.execv(__file__, sys.argv)
            sys.exit()

        if number == 'netinfo_refresh_ip':
            if ipversion == 'IPv4':
                ipversion = 'IPv6'
            else:
                ipversion = 'IPv4'
        print_menu_net(screen, matrix, ipversion)

    if number.startswith('services'):
        menu_pos = 2
        if number.startswith('services2'):
            print_menu_services(screen, matrix, service_matrix, 2)
        else:
            print_menu_services(screen, matrix, service_matrix, 1)
        if number == 'services_vnc':
            print('l')




# Set up the base menu you can customize your menu with the colors above

#set size of the screen
size = width, height = 480, 320
screen = pygame.display.set_mode(size)
pi_hostname = os.uname()[1]

background = pygame.image.load("imgs/Kali-Pi-3.5.jpg").convert()
screen.blit(background, [0,0])
pygame.display.update()
init_services(service_matrix)
time.sleep(2)
menu_pos = 1
print_menu1(screen, matrix, pi_hostname)

# Recollecting and printing data in background
dataBackground()

#While loop to manage touch screen inputs
while 1:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if screen_status:
                on_touch()
            else:
                screen_on()
                menu_pos = 1
                print_menu1(screen, matrix, pi_hostname)


        #ensure there is always a safe way to end the program if the touch screen fails
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                if not screen_status:
                    screen_on()
                    menu_pos = 1
                    print_menu1(screen, matrix, pi_hostname)
                if not menu_pos == 1:
                    menu_pos = 1
                    print_menu1(screen, matrix, pi_hostname)
                else:
                    pygame.quit()
                    sys.exit()
    pygame.display.update()
    ## Reduce CPU utilisation
    time.sleep(0.1)
