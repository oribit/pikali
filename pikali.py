#!/usr/bin/env python
import sys, os, time, threading, signal
import pygame
import subprocess

RASPB = 'arm' in os.uname()[4]

if RASPB:
    import RPi.GPIO as GPIO
'''
try:
    import RPi.GPIO as GPIO
except ImportError:
    pass
'''
import pikali_services
from pikali_screen import *
from pygame.locals import *


# Global variables
screen_status = 1 # 0 off 1 on
'''
menu_pos = 1 -> Entry
menu_pos = 2 -> Inside some menu
menu_pos = 100 -> Writing data
'''
menu_pos = 1 # Which menu is showing

ipversion = 'IPv4'
service_matrix = {}
# matrix (x, y, width, height, function_to_call)
matrix = []


class dataBackground(object):
    # Calculate different data in the background and display it. The update is every 5 seconds.

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
        global RASPB
        global screen, screen_status, menu_pos

        while True:
            if screen_status and menu_pos == 1:
                if RASPB:
                    screen.print_measure_data()
            # Always sleep!
            time.sleep(self.interval)

os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
os.environ["SDL_MOUSEDRV"] = "TSLIB"


def shutdown():
    pygame.quit()
    pikali_services.run_cmd("/usr/bin/sudo /sbin/shutdown -h now")
    sys.exit()


def restart():
    pygame.quit()
    pikali_services.run_cmd("/usr/bin/sudo /sbin/shutdown -r now")
    sys.exit()


def kill_process(process_name):
    process = Popen(('ps', '-A'), stdout=PIPE)
    output = process.communicate()[0]
    for line in output.split('\n'):
        line = line.split()
        if process_name in line:
            pid = int(line[0])
            os.kill(pid, signal.SIGKILL)


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

def refresh():
    pygame.quit()
    sys.exit()


def connect_wifi(wlan):
    """
    Connection to a wifi. If it's protected, it will ask for a password

    :param wlan:
    :return:
    """
    global menu_pos, screen

    pos, essid, extra_data = screen.get_screen_sel_list_current_value()
    if extra_data[essid]['Sec'] != 'None':
        # Wifi with password
        menu_pos = 100
        screen.print_entry_data('Introduce password', 'netinfo_' + wlan + '_wifipass_' + essid, 'netinfo_' + wlan + '_config')
    else:
        command = 'iwconfig ' + wlan + ' essid ' + essid
        output = pikali_services.run_cmd_shell(command)


def connect_wifi2(wlan, essid):
    """
    Connection to a protected wifi

    :param wlan:
    :return:
    """
    global screen

    p = screen.keyboard_text
    wpa_file = open('/tmp/wpa_supplicant.conf', 'w')
    data = '''network={{
        ssid="{}"
        psk="{}"
}}'''.format(essid.split(' ')[0], p)
    wpa_file.write(data + '\n')
    wpa_file.close()

    command = 'wpa_supplicant -B -D wext -i {} -c /tmp/wpa_supplicant.conf'.format(wlan)
    output = pikali_services.run_cmd_shell(command)
    print output
    time.sleep(2)
    command = 'dhclient {}'.format(wlan)
    output = pikali_services.run_cmd_shell(command)
    print output
    time.sleep(2)


def launch_host_apd(secure):
    global screen, menu_pos

    ssid = screen.keyboard_text
    data = ('interface=wlan1\n' +
            'driver=nl80211\n' +
            'ssid=' + ssid + '\n'
            'hw_mode=g\n' +
            'channel=6\n')

    if secure:
        menu_pos = 100
        screen.print_entry_data('INTRODUCE PASSWORD FOR SSID: ' + ssid, 'netinfo_hostapd_pass2_' + ssid, 'netinfo')
    else:
        hostapd_file = open('/tmp/hostapd.conf', 'w')
        hostapd_file.write(data)
        hostapd_file.close()
        command = 'hostapd -B /tmp/hostapd.conf'
        output = pikali_services.run_cmd_shell(command)
        print output


def launch_host_apd2(ssid):
    global screen

    passwd = screen.keyboard_text
    data = ('interface=wlan1\n' +
            'driver=nl80211\n' +
            'ssid=' + ssid + '\n'
            'hw_mode=g\n' +
            'channel=6\n' +
            'auth_algs=1\n' +
            'wpa=2\n' +
            'wpa_passphrase=' + passwd + '\n')
    hostapd_file = open('/tmp/hostapd.conf', 'w')
    hostapd_file.write(data)
    hostapd_file.close()
    for i in xrange(0, 2):
        # Let's try two times in case it didn't work first time
        command = 'hostapd -B /tmp/hostapd.conf'
        output = pikali_services.run_cmd_shell(command)
        print output
        if 'AP-ENABLED' in output:
            break


def run_iptables(enabled):
    if enabled:
        process = Popen(('sh', 'iptables.hostapd'), stdout=PIPE)
        output = process.communicate()[0]
        print output
    else:
        process = Popen(('iptables', '-F'), stdout=PIPE)
        output = process.communicate()[0]
        print output


def execute_action(number):
    """
    Define each possible action after screen interaction
    :param number:
    :return:
    """
    global screen
    global matrix
    global menu_pos, ipversion, service_matrix
    global pi_hostname

    screen.pdebug("action: " + str(number) +"\n")

    print 'ACTION:', action

    if number == '0':
        menu_pos = 2
        screen.clear_screen()
        screen.draw_image_touch('imgs/back.png', 'menu1', (10, 10), (80, 80))
        screen.draw_button("Refresh", 'refresh', 260, 30, 210, 55, colors['yellow'])
        screen.draw_button("Screen Off", 'screenoff', 260, 105, 210, 55, colors['yellow'])
        screen.draw_button("Reboot", 'reboot', 260, 180, 210, 55, colors['yellow'])
        screen.draw_button("Shutdown", 'shutdown', 260, 255, 210, 55, colors['yellow'])

    if number == 'xwin':
        menu_pos = 2
        screen.clear_screen()
        screen.draw_image_touch('imgs/back.png', 'menu1', (10, 10), (80, 80))
        screen.draw_button("X on TFT", 'xtft', 30, 230, 210, 55, colors['yellow'])
        screen.draw_button("X on HDMI", 'xhdmi', 260, 230, 210, 55, colors['yellow'])

    if number == 'xtft':
        # X TFT
        menu_pos = 0
        # To start XWindow, the display has to be "un-initialized", after executing this, it's not possible to recover pygame
        pygame.quit()

        # Using Popen and more important communicate, we wait for the end of startx
        cmd="/usr/bin/sudo FRAMEBUFFER=/dev/fb1 startx"
        process = Popen(cmd.split(), stdout=PIPE)
        output = process.communicate()[0]

        # We need to execute again the program, it's the only way to reinitialize everything
        os.execv(__file__, sys.argv)

    if number == 'xhdmi':
        # X HDMI
        menu_pos = 0
        # Read comments from X TFT
        pygame.quit()
        cmd="/usr/bin/sudo FRAMEBUFFER=/dev/fb0 startx"
        process = Popen(cmd.split(), stdout=PIPE)
        output = process.communicate()[0]

        os.execv(__file__, sys.argv)

    if number == 'shell':
        # exit
        pygame.quit()
        #process = subprocess.call("setterm -term linux -back default -fore white -clear all", shell=True)
        sys.exit(33)

    if number == 'screenoff':
        menu_pos = 0
        screen_off()

    if number == 'shutdown':
        shutdown()

    if number == 'reboot':
        restart()

    if number == 'refresh':
        refresh()

    if number == 'menu1':
        menu_pos = 1
        screen.print_menu1(pi_hostname)

    if number.startswith('netinfo'):
        menu_pos = 2
        '''
        This needs to be rebuilt
        
        if number == 'netinfo_kismet':
            pygame.quit()
            subprocess.call("/usr/bin/kismet")
            os.execv(__file__, sys.argv)
            sys.exit()

        if number == 'netinfo_sdr':
            pygame.quit()
            cmd="/bin/bash " + os.path.dirname(os.path.abspath(__file__)) + "/sdr-scanner.sh"
            process = Popen(cmd.split(), stdout=PIPE)
            output = process.communicate()[0]
            os.execv(__file__, sys.argv)
            sys.exit()
        '''

        if number == 'netinfo_refresh_ip':
            if ipversion == 'IPv4':
                ipversion = 'IPv6'
            else:
                ipversion = 'IPv4'

        elif number == 'netinfo_wifi':
            screen.print_menu_wifi()
        elif number.startswith('netinfo_wlan'):
            if 'config' in number:
                screen.print_menu_wifi_config(number.split('_')[1])
                screen.print_extra_data_wifi()
            elif 'connect' in number:
                connect_wifi(number.split('_')[1])
            elif 'pass' in number:
                # The format here is: netinfo_wlanX_password_<essid>
                connect_wifi2(number.split('_')[1], ''.join(number.split('_')[3:]))
                screen.print_menu_wifi()
            else:
                screen.print_menu_wifi_wlan(number.split('_')[1])
        elif number.startswith('netinfo_hostapd'):
            if 'pass2' in number:
                # Format is 'netinfo_hostapd_pass2_' + ssid
                launch_host_apd2(''.join(number.split('_')[3:]))
                screen.print_menu_net()
            elif 'pass' in number:
                screen.print_menu_hostapd()
            elif 'open' in number:
                launch_host_apd(False)
                screen.print_menu_net()
            elif 'secure' in number:
                launch_host_apd(True)
            else:
                menu_pos = 100
                screen.print_entry_data('INTRODUCE SSID NAME', 'netinfo_hostapd_pass', 'netinfo')
        elif number.startswith('netinfo_iptables'):
            if 'enable' in number:
                run_iptables(True)
                screen.print_menu_net(ipversion)
            elif 'disable' in number:
                run_iptables(False)
                screen.print_menu_net(ipversion)
            else:
                screen.print_menu_iptables()
        else:
            screen.print_menu_net(ipversion)

    if number.startswith('services'):
        menu_pos = 2
        if number.startswith('services2'):
            screen.print_menu_services(service_matrix, 2)
        else:
            if number == 'services_vnc':
                if service_matrix['vnc'] == 'off':
                    service_matrix['vnc'] = 'on'
                    pikali_services.start_service_vnc()
                else:
                    service_matrix['vnc'] = 'off'
                    pikali_services.stop_service_vnc()
            elif number == 'services_apache':
                if service_matrix['apache'] == 'off':
                    service_matrix['apache'] = 'on'
                    pikali_services.start_service_apache()
                else:
                    service_matrix['apache'] = 'off'
                    pikali_services.stop_service_apache()
            elif number == 'services_pureftp':
                if service_matrix['pureftp'] == 'off':
                    service_matrix['pureftp'] = 'on'
                    pikali_services.start_service_pureftp()
                else:
                    service_matrix['pureftp'] = 'off'
                    pikali_services.stop_service_pureftp()
            elif number == 'services_hostapd':
                if service_matrix['hostapd'] == 'on':
                    service_matrix['hostapd'] = 'off'
                    kill_process('hostapd')
            elif number == 'services_dnsmasq':
                if service_matrix['dnsmasq'] == 'off':
                    service_matrix['dnsmasq'] = 'on'
                    pikali_services.start_service_dnsmasq()
                else:
                    service_matrix['dnsmasq'] = 'off'
                    pikali_services.stop_service_dnsmasq()


            time.sleep(1) # Time for starting services
            screen.print_menu_services(service_matrix, 1)

    if number.startswith('sellist'):
        screen.refresh_selection_list(number.split('-')[1])
        screen.print_extra_data_wifi()


####################################################################
#                                                                  #
#                               MAIN                               #
#                                                                  #
####################################################################


PDEBUG = os.environ.get('PIKALIDEBUG') == 'ON'

# Initialize pygame modules individually (to avoid ALSA errors) and hide mouse

screen = Screen()
#pygame.font.init()
#pygame.display.init()

if RASPB:
    pygame.mouse.set_visible(0)
else:
    pygame.mouse.set_visible(1)

#size = width, height = 480, 320
#screen = pygame.display.set_mode(size)
pi_hostname = os.uname()[1]

background = pygame.image.load("imgs/Kali-Pi-3.5.jpg").convert()
screen.surface.blit(background, [0,0])
pygame.display.update()
pikali_services.init_services(service_matrix)
time.sleep(2)
menu_pos = 1
screen.print_menu1(pi_hostname)

# Recollecting and printing data in background
dataBackground()

#While loop to manage touch screen inputs
while 1:
    for event in pygame.event.get():
        if menu_pos == 100:
            screen.keyboard_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if screen_status:
                action = screen.on_touch()
                if action:
                    execute_action(action)
            else:
                screen_on()
                menu_pos = 1
                screen.print_menu1(pi_hostname)


        #ensure there is always a safe way to end the program if the touch screen fails
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                if not screen_status:
                    screen_on()
                    menu_pos = 1
                    screen.print_menu1(pi_hostname)
                if not menu_pos == 1:
                    menu_pos = 1
                    screen.print_menu1(pi_hostname)
                else:
                    pygame.quit()
                    sys.exit()
    pygame.display.update()
    ## Reduce CPU utilization
    time.sleep(0.1)
