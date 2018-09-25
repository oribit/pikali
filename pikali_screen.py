"""
Pygame Keyboard from: https://github.com/Faylixe/pygame_vkeyboard

"""

import pygame, sys, os
import pikali_services
from subprocess import Popen, PIPE
from pygame.locals import *

from vkeyboard import *

RASPB = 'arm' in os.uname()[4]

colors = {}
# colors                R    G    B
colors['white']    = (255, 255, 255)
colors['black']    = (  0,   0,   0)
colors['red']      = (255,   0,   0)
colors['green']    = (  0, 255,   0)
colors['blue']     = (  0,   0, 255)
colors['cyan']     = ( 50, 255, 255)
colors['magenta']  = (255,   0, 255)
colors['yellow']   = (255, 255,   0)
colors['orange']   = (255, 127,   0)
colors['grey']     = (128, 128, 128)


class SelectionList:
    def __init__(self, data, extra_data, pos=0, sel_down=0, sel_up=4, x=0, y=0, width=0, height=110, color=colors['blue']):
        self.pos = pos
        self.sel_down = sel_down
        self.sel_up = sel_up
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.data = data
        self.extra_data = extra_data

    def current_value(self):
        return self.data[self.pos]

class Screen:
    def __init__(self, size=(480, 320)):
        pygame.font.init()
        pygame.display.init()
        self.size = size
        self.surface = pygame.display.set_mode(size)
        self.matrix = []
        self.DEBUG = False
        self.widget = {}
        self.keyboard_text = ''

    def clear_screen(self):
        """
        Completely black and empty screen
        :return:
        """
        self.fill(colors['black'])
        self.matrix = []

    def on_touch(self):
        """
        Define a function that checks for touch location. Using position matrix for that.

        :return:
        """
        # get the position that was touched
        action = None
        touch_pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        self.pdebug(str("MOUSE X: " + str(pygame.mouse.get_pos()[0]) + " MOUSE Y: " + str(pygame.mouse.get_pos()[1]) + "\n"))
        self.pdebug(str(str(self.matrix) + "\n"))
        # matrix (x, y, width, height, function_to_call)
        for i in range(len(self.matrix)):
            x = self.matrix[i][0]
            y = self.matrix[i][1]
            max_x = x + self.matrix[i][2]
            max_y = y + self.matrix[i][3]
            if x <= touch_pos[0] <= max_x and y <= touch_pos[1] <= max_y:
                action = self.matrix[i][4]
                break

        return action

    def fill(self, color):
        """
        Fill the screen with one color

        :param color:
        :return:
        """
        self.surface.fill(color)

    def draw_image(self, image, pos, resize=(0,0)):
        """
        Draw an image into the surface

        :param image: String with the image path
        :param pos: TUPLE with X, Y position
        :param resize: TUPLE with the new size in case we want to resize image
        :return:
        """
        icon = pygame.image.load(image)
        if resize != (0,0):
            icon = pygame.transform.scale(icon, resize)
        self.surface.blit(icon, list(pos))

    def draw_image_touch(self, image, action, pos, size):
        """
        Same as draw_image but it takes the image as "touchable"

        :param action: Action to be executed when the image is touched
        :param image: String with the image path
        :param pos: TUPLE with X,Y position
        :param size: TUPLE with the size
        :return:
        """
        self.matrix.append([pos[0], pos[1], size[0], size[1], action])
        self.draw_image(image, pos, size)

    def draw_label(self, text, xpo, ypo, fontsize, color):
        font = pygame.font.Font(None, fontsize)
        label = font.render(str(text), 1, (color))
        self.surface.blit(label, (xpo, ypo))

    def draw_button(self, text, action, xpo, ypo, width, height, color):
        """
        Printing text in a specific place with a specific width and height with a specific color and border

        :param text:
        :param xpo:
        :param ypo:
        :param width:
        :param height:
        :param color:
        :return:
        """
        pygame.draw.rect(self.surface, color, (xpo - 10, ypo - 10, width, height), 3)
        pygame.draw.rect(self.surface, color, (xpo - 9, ypo - 9, width - 1, height - 1), 1)
        pygame.draw.rect(self.surface, color, (xpo - 8, ypo - 8, width - 2, height - 2), 1)
        font = pygame.font.Font(None, height - 5)
        text = str(text)
        # Let's say 15 per char
        if len(text) * 15 < width:
            space = width / 15
            space_left = space - len(text)
            for i in xrange(1, (space_left / 2)):
                text = ' ' + text

        label = font.render(str(text), 1, (color))
        self.surface.blit(label, (xpo, ypo))
        self.matrix.append([xpo, ypo, width, height, action])

    def print_measure_data(self):
        """
        Print temperature

        :return:
        """
        command = "vcgencmd measure_temp"
        process = Popen(command.split(), stdout=PIPE)
        output = process.communicate()[0]
        temp = 'Temp: ' + output.decode()[5:-1]
        r = pygame.draw.rect(self.surface, colors['black'], (210, 20, 150, 30), 1)
        self.surface.fill(colors['black'], r)
        self.draw_label(temp, 210, 20, 32, colors['orange'])

    def print_menu1(self, pi_hostname):
        """
        Print initial menu

        :param pi_hostname:
        :return:
        """
        self.clear_screen()

        # Printing hostname
        self.draw_label(pi_hostname, 32, 30, 48, colors['magenta'])

        # Shutdown button
        self.draw_image_touch('imgs/shutdown-icon-33.png', '0', (410, 20), (60, 60))

        # Printing measurement data
        if RASPB:
            self.print_measure_data()

        self.draw_image_touch('imgs/net.png', 'netinfo', (30, 90), (80, 80))
        self.draw_image_touch('imgs/xwin.png', 'xwin', (120, 90), (80, 80))
        self.draw_image_touch('imgs/shell.png', 'shell', (210, 90), (80, 80))
        self.draw_image_touch('imgs/servers.png', 'services', (300, 90), (80, 80))
        self.draw_image_touch('imgs/metasploit.png', 'metasploit', (30, 180), (80, 80))
        self.draw_image_touch('imgs/nmap_logo.png', 'nmap', (120, 180), (80, 80))

    def print_menu_net(self, ipversion):
        """
        Print network menu

        :param ipversion:
        :return:
        """
        self.clear_screen()
        self.draw_image_touch('imgs/back.png', 'menu1', (10, 10), (80, 80))
        self.draw_image_touch('imgs/ipv4ipv6.png', 'netinfo_refresh_ip', (390, 10), (80, 60))
        self.draw_image_touch('imgs/wifi.png', 'netinfo_wifi', (390, 80), (60, 60))
        self.draw_image_touch('imgs/kismet.png', 'netinfo_kismet', (390, 160), (60, 70))
        self.draw_image_touch('imgs/sdr.png', 'netinfo_sdr', (390, 240), (60, 70))

        # Printing IP
        command = 'ip addr | grep "inet\|BROAD" | grep -v "127.0.0.1\|::1/128"'
        process = Popen(command, stdout=PIPE, shell=True)
        output = process.communicate()[0]
        output = output.split("\n")
        hzn = 100
        for line in output:
            if line:
                if "BROADCAST" in line or "broadcast" in line:
                    line = line.split(":")
                    self.draw_label("Int: " + str(line[1]), 30, hzn, 24, colors['yellow'])
                    hzn += 30
                else:
                    if "inet6" in line and ipversion == 'IPv6':
                        line = line.split()
                        self.draw_label("IPv6: " + str(line[1]), 30, hzn, 24, colors['yellow'])
                        hzn += 30
                    elif not ("inet6" in line) and ipversion == 'IPv4':
                        line = line.split()
                        self.draw_label("IPv4: " + str(line[1]), 30, hzn, 24, colors['yellow'])
                        hzn += 30

    def print_menu_services(self, service_matrix, page):
        pikali_services.check_service(service_matrix)

        self.clear_screen()
        if page == 1:
            service_s = 'Hostapd'
        elif page == 2:
            service_s = 'Openvas'

        self.matrix.append([5, 10, 200, 60, 'services_' + service_s.lower()])
        iconf = "imgs/" + service_s + ".png"
        iconf = iconf.lower()
        icon = pygame.image.load(iconf)
        icon = pygame.transform.scale(icon, (60, 60))
        self.surface.blit(icon, [5, 10])
        if service_matrix[service_s.lower()] == 'on':
            self.draw_label(service_s, 70, 30, 32, colors['green'])
            icon = pygame.image.load("imgs/swon.png")
            icon = pygame.transform.scale(icon, (40, 20))
        else:
            self.draw_label(service_s, 70, 30, 32, colors['red'])
            icon = pygame.image.load("imgs/swoff.png")
            icon = pygame.transform.scale(icon, (40, 20))
        self.surface.blit(icon, [180, 30])

        if page == 1:
            service_s = 'Apache'
        elif page == 2:
            service_s = 'Snort'
        self.matrix.append([5, 130, 200, 60, 'services_' + service_s.lower()])
        iconf = "imgs/" + service_s + ".png"
        iconf = iconf.lower()
        icon = pygame.image.load(iconf)
        icon = pygame.transform.scale(icon, (60, 60))
        self.surface.blit(icon, [5, 130])
        if service_matrix[service_s.lower()] == 'on':
            self.draw_label(service_s, 70, 150, 32, colors['green'])
            icon = pygame.image.load("imgs/swon.png")
            icon = pygame.transform.scale(icon, (40, 20))
        else:
            self.draw_label(service_s, 70, 150, 32, colors['red'])
            icon = pygame.image.load("imgs/swoff.png")
            icon = pygame.transform.scale(icon, (40, 20))
        self.surface.blit(icon, [180, 150])

        if page == 1:
            service_s = 'PureFTP'
            self.matrix.append([240, 10, 200, 60, 'services_' + service_s.lower()])
            iconf = "imgs/" + service_s + ".png"
            iconf = iconf.lower()
            icon = pygame.image.load(iconf)
            icon = pygame.transform.scale(icon, (60, 60))
            self.surface.blit(icon, [240, 10])
            if service_matrix[service_s.lower()] == 'on':
                self.draw_label(service_s, 305, 30, 32, colors['green'])
                icon = pygame.image.load("imgs/swon.png")
                icon = pygame.transform.scale(icon, (40, 20))
            else:
                self.draw_label(service_s, 305, 30, 32, colors['red'])
                icon = pygame.image.load("imgs/swoff.png")
                icon = pygame.transform.scale(icon, (40, 20))
            self.surface.blit(icon, [415, 30])

        if page == 1:
            service_s = 'VNC'
            self.matrix.append([240, 130, 200, 60, 'services_' + service_s.lower()])
            iconf = "imgs/" + service_s + ".png"
            iconf = iconf.lower()
            icon = pygame.image.load(iconf)
            icon = pygame.transform.scale(icon, (60, 60))
            self.surface.blit(icon, [240, 130])
            if service_matrix['vnc'] == 'on':
                self.draw_label(service_s, 305, 150, 32, colors['green'])
                icon = pygame.image.load("imgs/swon.png")
                icon = pygame.transform.scale(icon, (40, 20))
            else:
                self.draw_label(service_s, 305, 150, 32, colors['red'])
                icon = pygame.image.load("imgs/swoff.png")
                icon = pygame.transform.scale(icon, (40, 20))
            self.surface.blit(icon, [415, 150])

        # Arrows
        if page == 1:
            self.matrix.append([5, 250, 70, 70, 'menu1'])
        elif page == 2:
            self.matrix.append([5, 250, 70, 70, 'services'])
        icon = pygame.image.load("imgs/back.png")
        icon = pygame.transform.scale(icon, (70, 70))
        self.surface.blit(icon, [5, 250])

        self.matrix.append([205, 250, 70, 70, 'menu1'])
        icon = pygame.image.load("imgs/top.png")
        icon = pygame.transform.scale(icon, (70, 70))
        self.surface.blit(icon, [205, 250])

        if page == 1:
            self.matrix.append([410, 250, 70, 70, 'services2'])
            icon = pygame.image.load("imgs/next.png")
            icon = pygame.transform.scale(icon, (70, 70))
            self.surface.blit(icon, [410, 250])

    def print_menu_wifi(self):
        """
        Print Menu to choose WLAN interface

        :return:
        """
        self.clear_screen()
        self.draw_image_touch('imgs/back.png', 'netinfo', (10, 10), (80, 80))
        self.draw_image_touch('imgs/wifi.png', 'netinfo_wlan0', (120, 120), (80, 80))
        self.draw_label('wlan0', 125, 210, 32, colors['green'])
        self.draw_image_touch('imgs/wifi.png', 'netinfo_wlan1', (320, 120), (80, 80))
        self.draw_label('wlan1', 325, 210, 32, colors['green'])

    def print_menu_wifi_wlan(self, wifi):
        """
        Print specific information about WLAN interface choosen

        :param wifi: wlan interface choosen
        :return:
        """
        self.clear_screen()
        self.draw_image_touch('imgs/back.png', 'netinfo_wifi', (10, 10), (60, 60))
        self.draw_image_touch('imgs/config.png', 'netinfo_' + wifi + '_config', (390, 10), (60, 60))

        # Printing IP
        command = 'iwconfig ' + wifi

        process = Popen(command, stdout=PIPE, shell=True)
        output = process.communicate()[0]
        output = output.split("\n")
        wlan = ''
        wlan_d = {}
        hzn = 100
        for line in output:
            line = line.strip()
            if line.startswith('wlan'):
                wlan = line.split(' ')[0].strip()
                wlan_d[wlan] = {}
                wlan_d[wlan]['essid'] = line.split('ESSID')[1][2:-1]
            if 'Frequency' in line:
                t_line = line.split(' ')
                wlan_d[wlan]['frequency'] = ''.join([x for x in t_line if x.startswith('Frequency')]).split(':')[1]
            if 'Access Point' in line:
                t_line = line.split(' ')
                wlan_d[wlan]['mac_ap'] = t_line[-1]

        for wlan, data in wlan_d.iteritems():
            self.draw_label(wlan, 30, hzn, 24, colors['yellow'])
            hzn += 30
            for k, v in data.iteritems():
                self.draw_label(k + ': ' + v, 30, hzn, 24, colors['yellow'])
                hzn += 30

    def print_menu_wifi_config(self, wifi):
        """
        Print configuration wifi menu

        :param wifi:
        :return:
        """
        self.clear_screen()
        self.draw_image_touch('imgs/back.png', 'netinfo_wifi', (10, 10), (60, 60))
        self.draw_image_touch('imgs/check_mark.png', 'netinfo_' + wifi + '_connect', (390, 10), (60, 60))

        essid_list = []
        # Printing IP
        if RASPB:
            command = 'iwlist ' + wifi + ' scanning'
            process = Popen(command, stdout=PIPE, shell=True)
            output = process.communicate()[0]
            print output
            output = output.split("\n")
        else:
            output = open('test_iwlist.output')

        secure = False
        enc_type = ''
        essid = '-1<'
        extra_data = {}
        t_data = {}
        for line in output:
            line = line.strip()
            if line.startswith("Cell"):
                if essid != '-1<':
                    if secure:
                        essid += '  *'
                        if 'Sec' not in t_data:
                            t_data['Sec'] = 'Unkown'
                    else:
                        t_data['Sec'] = 'None'
                    essid_list.append(essid)
                    extra_data[essid] = t_data
                    t_data = {}
                secure = False
                enc_type = ''
                t_data['address'] = line.split('Address')[1][1:].strip()
            if line.startswith("ESSID"):
                essid = line.split('"')[1]
            elif line.startswith("Encryption"):
                if line.split(':')[1].strip() == "on":
                    secure = True
            elif line.startswith("Channel"):
                t_data['chanel'] = line.split(':')[1].strip()
            elif line.startswith("Quality"):
                t_data['quality'] = line.split('Quality=')[1].strip()
            elif line.startswith("IE") and secure:
                if 'WPA' in line:
                    if 'WPA2 Version' in line:
                        if 'Sec' not in t_data:
                            t_data['Sec'] = 'WPA2'
                        else:
                            t_data['Sec'] += '/WPA2'
                    if 'WPA Version 1' in line:
                        if 'Sec' not in t_data:
                            t_data['Sec'] = 'WPA'
                        else:
                            t_data['Sec'] += '/WPA'
                    if 'Authentication Suites' in line and '802.1x':
                        if 'WPA2' in t_data['Sec']:
                            t_data['Sec'] = t_data['Sec'].replace('WPA2', 'WPA2 (802.1x)')
                        elif 'WPA' in t_data['Sec']:
                            t_data['Sec'] = t_data['Sec'].replace('WPA', 'WPA (802.1x)')

        essid_list.append(essid)
        extra_data[essid] = t_data
        self.draw_selection_list(essid_list, extra_data, 10, 80, 460, colors['blue'])

    def draw_selection_list(self, list_data, extra_data, xpo, ypo, width, color):
        if 'sel_list' in self.widget:
            del self.widget['sel_list']

        self.widget['sel_list'] = SelectionList(data=list_data, extra_data=extra_data, x=xpo, y=ypo, width=width, color=color)

        pygame.draw.rect(self.surface, color, (self.widget['sel_list'].x - 1, self.widget['sel_list'].y - 1, self.widget['sel_list'].width, self.widget['sel_list'].height), 3)
        pygame.draw.rect(self.surface, color, (self.widget['sel_list'].x, self.widget['sel_list'].y, self.widget['sel_list'].width - 1, self.widget['sel_list'].height - 1), 1)
        hzn = self.widget['sel_list'].y + 5

        for i in xrange(self.widget['sel_list'].sel_down, self.widget['sel_list'].sel_up):
            if len(self.widget['sel_list'].data) >= i + 1:
                if i == int(self.widget['sel_list'].pos):
                    pygame.draw.line(self.surface, colors['grey'], [self.widget['sel_list'].x + 5, hzn + 5], [self.widget['sel_list'].x + 5 + self.widget['sel_list'].width - 52, hzn + 5], 20)
                else:
                    pygame.draw.line(self.surface, colors['black'], [self.widget['sel_list'].x + 5, hzn + 5], [self.widget['sel_list'].x + 5 + self.widget['sel_list'].width - 52, hzn + 5], 20)
                self.draw_label(self.widget['sel_list'].data[i], self.widget['sel_list'].x + 5, hzn, 24, colors['yellow'])
                # Each "text" added can be "clicked", we need to addid to the matrix
                self.matrix.append([self.widget['sel_list'].x + 2, hzn - 2, self.widget['sel_list'].width - 52, 20, 'sellist-' + str(i)])
                hzn += 25

        if len(self.widget['sel_list'].data) > 4:
            icon = pygame.image.load("imgs/arrow_up.png")
            icon = pygame.transform.scale(icon, (50, 50))
            self.surface.blit(icon, [self.widget['sel_list'].x + self.widget['sel_list'].width - 52, self.widget['sel_list'].y + 3])
            self.matrix.append([self.widget['sel_list'].x + self.widget['sel_list'].width - 52, self.widget['sel_list'].y + 3, 50, 50, 'sellist-up'])
            icon = pygame.image.load("imgs/arrow_down.png")
            icon = pygame.transform.scale(icon, (50, 50))
            self.surface.blit(icon, [self.widget['sel_list'].x + self.widget['sel_list'].width - 52, self.widget['sel_list'].y + (2 * 24)])
            self.matrix.append([self.widget['sel_list'].x + self.widget['sel_list'].width - 52, self.widget['sel_list'].y + (2 * 24), 50, 50, 'sellist-down'])

    def refresh_selection_list(self, sel_pos):
        if sel_pos == 'up':
            if self.widget['sel_list'].pos > 0:
                self.widget['sel_list'].pos -= 1
            if self.widget['sel_list'].pos < self.widget['sel_list'].sel_down:
                self.widget['sel_list'].sel_down -= 1
                self.widget['sel_list'].sel_up -= 1
        elif sel_pos == 'down':
            if self.widget['sel_list'].pos < len(self.widget['sel_list'].data) - 1:
                self.widget['sel_list'].pos += 1
            if self.widget['sel_list'].sel_up - 1 < self.widget['sel_list'].pos:
                self.widget['sel_list'].sel_down += 1
                self.widget['sel_list'].sel_up += 1
        else:
            self.widget['sel_list'].pos = int(sel_pos)

        hzn = self.widget['sel_list'].y + 5
        for i in xrange(self.widget['sel_list'].sel_down, self.widget['sel_list'].sel_up):
            if len(self.widget['sel_list'].data) >= i + 1:
                if i == int(self.widget['sel_list'].pos):
                    pygame.draw.line(self.surface, colors['grey'], [self.widget['sel_list'].x + 5, hzn + 7], [self.widget['sel_list'].x + 5 + self.widget['sel_list'].width - 52, hzn + 7], 24)
                else:
                    pygame.draw.line(self.surface, colors['black'], [self.widget['sel_list'].x + 5, hzn + 7], [self.widget['sel_list'].x + 5 + self.widget['sel_list'].width - 52, hzn + 7], 24)
                self.draw_label(self.widget['sel_list'].data[i], self.widget['sel_list'].x + 5, hzn, 24, colors['yellow'])
                # Each "text" added can be "clicked", we need to addid to the matrix
                self.matrix.append([self.widget['sel_list'].x + 2, hzn - 2, self.widget['sel_list'].width - 52, 20, 'sellist-' + str(i)])
                hzn += 25

    def get_screen_sel_list_current_value(self):
        return self.widget['sel_list'].pos, self.widget['sel_list'].current_value(), self.widget['sel_list'].extra_data

    def print_extra_data_wifi(self):
        extra_data = self.widget['sel_list'].extra_data[self.widget['sel_list'].current_value()]
        hzn = 200
        key_list = sorted(extra_data.keys())
        pygame.draw.line(self.surface, colors['black'], [10, 215], [480, 215], 40)
        pygame.draw.line(self.surface, colors['black'], [10, 250], [480, 250], 40)
        pygame.draw.line(self.surface, colors['black'], [10, 290], [480, 290], 40)
        for k in key_list:
            self.draw_label(k + ': ' + extra_data[k], 10, hzn, 22, colors['yellow'])
            hzn += 22

    def print_entry_data(self, title, save, previous):
        """
        Load the screen for taking some data using the interactive keyboard

        :param title: Title will be displayed in the top
        :param save: Action to be executed when "Ok" is pressed
        :param previous: Action to be executed when "Back" is pressed
        :return:
        """
        self.clear_screen()
        self.draw_image_touch('imgs/back.png', previous, (10, 10), (60, 60))
        self.draw_image_touch('imgs/check_mark.png', save, (390, 10), (60, 60))

        self.draw_label(title, 90, 10, 22, colors['yellow'])

        self.draw_button('', '', 10, 80, 470, 80, colors['blue'])

        layout = VKeyboardLayout(VKeyboardLayout.AZERTY)
        self.widget['keyboard'] = VKeyboard(self.surface, self.keyboard_consumer, layout)
        self.widget['keyboard'].enable()

    def keyboard_event(self, event):
        self.widget['keyboard'].on_event(event)

    def keyboard_consumer(self, text):
        self.keyboard_text = str(text)
        pygame.draw.line(self.surface, colors['black'], (12, 82), (472, 82), 22)
        self.draw_label(text, 12, 82, 22, colors['yellow'])

    def pdebug(self, text):
        if self.DEBUG:
            print sys.stderr.write(text)


