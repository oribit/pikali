import pygame, sys
import pikali_services
from subprocess import Popen, PIPE
from pygame.locals import *

DARWIN = sys.platform == "darwin"

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
    def __init__(self, data, pos=0, sel_down=0, sel_up=4, x=0, y=0, width=0, height=100, color=colors['blue']):
        self.pos = pos
        self.sel_down = sel_down
        self.sel_up = sel_up
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.data = data

screen_sel_list = None

def pdebug(PDEBUG, text):
    if PDEBUG:
        print sys.stderr.write(text)


def run_cmd(cmd):
    process = Popen(cmd.split(), stdout=PIPE)
    output = process.communicate()[0]
    return output


def run_cmd_shell(cmd):
    process = Popen(cmd.split(), stdout=PIPE, shell=True)
    output = process.communicate()[0]
    return output


def print_measure_data(screen):
    command = "vcgencmd measure_temp"
    process = Popen(command.split(), stdout=PIPE)
    output = process.communicate()[0]
    temp = 'Temp: ' + output.decode()[5:-1]
    r = pygame.draw.rect(screen, colors['black'], (210,20, 150, 30),1)
    screen.fill(colors['black'], r)
    draw_label(screen, temp, 210, 20, 32, colors['orange'])


def draw_selection_list(screen, matrix, list_data, xpo, ypo, width, color):
    global screen_sel_list

    del screen_sel_list
    screen_sel_list = SelectionList(data=list_data, x=xpo, y=ypo, width=width, color=color)

    pygame.draw.rect(screen, color, (screen_sel_list.x - 1, screen_sel_list.y - 1, screen_sel_list.width, screen_sel_list.height), 3)
    pygame.draw.rect(screen, color, (screen_sel_list.x, screen_sel_list.y, screen_sel_list.width - 1, screen_sel_list.height - 1), 1)
    hzn = screen_sel_list.y + 5

    for i in xrange(screen_sel_list.sel_down, screen_sel_list.sel_up):
        if len(screen_sel_list.data) >= i + 1:
            if i == int(screen_sel_list.pos):
                pygame.draw.line(screen, colors['grey'], [screen_sel_list.x + 5, hzn + 5], [screen_sel_list.x + 5 + screen_sel_list.width - 32, hzn + 5], 20)
                #pygame.draw.rect(screen, colors['grey'], (xpo + 5, hzn, width - 32, 16), 3)
            else:
                pygame.draw.line(screen, colors['black'], [screen_sel_list.x + 5, hzn + 5], [screen_sel_list.x + 5 + screen_sel_list.width - 32, hzn + 5], 20)
            draw_label(screen, screen_sel_list.data[i], screen_sel_list.x + 5, hzn, 24, colors['yellow'])
            # Each "text" added can be "clicked", we need to addid to the matrix
            #pygame.draw.rect(screen, color, (xpo + 2, hzn - 2, width - 28, 20), 1)
            matrix.append([screen_sel_list.x + 2, hzn - 2, screen_sel_list.width - 28, 20, 'sellist-' + str(i)])
            hzn += 25

    if len(screen_sel_list.data) > 4:
        icon = pygame.image.load("imgs/arrow_up.png")
        icon = pygame.transform.scale(icon, (25, 25))
        screen.blit(icon, [screen_sel_list.x + screen_sel_list.width - 27, screen_sel_list.y + 3])
        matrix.append([screen_sel_list.x + screen_sel_list.width - 27, screen_sel_list.y + 3, 25, 25, 'sellist-up'])
        icon = pygame.image.load("imgs/arrow_down.png")
        icon = pygame.transform.scale(icon, (25, 25))
        screen.blit(icon, [screen_sel_list.x + screen_sel_list.width - 27, screen_sel_list.y + (3 * 24)])
        matrix.append([screen_sel_list.x + screen_sel_list.width - 27, screen_sel_list.y + (3 * 24), 25, 25, 'sellist-down'])


def refresh_selection_list(screen, matrix, sel_pos):
    global screen_sel_list

    if sel_pos == 'up':
        if screen_sel_list.pos > 0:
            screen_sel_list.pos -= 1
        if screen_sel_list.pos < screen_sel_list.sel_down:
            screen_sel_list.sel_down -= 1
            screen_sel_list.sel_up -= 1
    elif sel_pos == 'down':
        if screen_sel_list.pos < len(screen_sel_list.data) - 1:
            screen_sel_list.pos += 1
        if screen_sel_list.sel_up - 1 < screen_sel_list.pos:
            screen_sel_list.sel_down += 1
            screen_sel_list.sel_up += 1
    else:
        screen_sel_list.pos = int(sel_pos)

    hzn = screen_sel_list.y + 5
    for i in xrange(screen_sel_list.sel_down, screen_sel_list.sel_up):
        if len(screen_sel_list.data) >= i + 1:
            if i == int(screen_sel_list.pos):
                pygame.draw.line(screen, colors['grey'], [screen_sel_list.x + 5, hzn + 7], [screen_sel_list.x + 5 + screen_sel_list.width - 32, hzn + 7], 24)
                #pygame.draw.rect(screen, colors['grey'], (xpo + 5, hzn, width - 32, 16), 3)
            else:
                pygame.draw.line(screen, colors['black'], [screen_sel_list.x + 5, hzn + 7], [screen_sel_list.x + 5 + screen_sel_list.width - 32, hzn + 7], 24)
            draw_label(screen, screen_sel_list.data[i], screen_sel_list.x + 5, hzn, 24, colors['yellow'])
            # Each "text" added can be "clicked", we need to addid to the matrix
            #pygame.draw.rect(screen, color, (xpo + 2, hzn - 2, width - 28, 20), 1)
            matrix.append([screen_sel_list.x + 2, hzn - 2, screen_sel_list.width - 28, 20, 'sellist-' + str(i)])
            hzn += 25

    if len(screen_sel_list.data) > 4:
        icon = pygame.image.load("imgs/arrow_up.png")
        icon = pygame.transform.scale(icon, (25, 25))
        screen.blit(icon, [screen_sel_list.x + screen_sel_list.width - 27, screen_sel_list.y + 3])
        matrix.append([screen_sel_list.x + screen_sel_list.width - 27, screen_sel_list.y + 3, 25, 25, 'sellist-up'])
        icon = pygame.image.load("imgs/arrow_down.png")
        icon = pygame.transform.scale(icon, (25, 25))
        screen.blit(icon, [screen_sel_list.x + screen_sel_list.width - 27, screen_sel_list.y + (3 * 24)])
        matrix.append([screen_sel_list.x + screen_sel_list.width - 27, screen_sel_list.y + (3 * 24), 25, 25, 'sellist-down'])

    pygame.draw.rect(screen, screen_sel_list.color, (screen_sel_list.x - 1, screen_sel_list.y - 1, screen_sel_list.width, screen_sel_list.height), 3)
    pygame.draw.rect(screen, screen_sel_list.color, (screen_sel_list.x, screen_sel_list.y, screen_sel_list.width - 1, screen_sel_list.height - 1), 1)


def draw_button(screen, text, xpo, ypo, width, height, color):
    '''
    Printing text in a specific place with a specific width and height with a specific color and border    
    :param screen: 
    :param text: 
    :param xpo: 
    :param ypo: 
    :param width: 
    :param height: 
    :param color: 
    :return: 
    '''
    pygame.draw.rect(screen, color, (xpo-10,ypo-10,width,height),3)
    pygame.draw.rect(screen, color, (xpo-9,ypo-9,width-1,height-1),1)
    pygame.draw.rect(screen, color, (xpo-8,ypo-8,width-2,height-2),1)
    font=pygame.font.Font(None,42)
    label=font.render(str(text), 1, (color))
    screen.blit(label,(xpo,ypo))


# define function for printing text in a specific place with a specific color
def draw_label(screen, text, xpo, ypo, fontsize, color):
    font=pygame.font.Font(None,fontsize)
    label=font.render(str(text), 1, (color))
    screen.blit(label,(xpo,ypo))


def print_menu1(screen, matrix, pi_hostname):
    # Background Color
    screen.fill(colors['black'])

    # Matrix is a mutable object, but if we assign to a value, Python will
    # create a new object. We need to use "functions" to change its value
    # matrix = [] -> This will not work
    del matrix[:]

    # Printing hostname
    draw_label(screen, pi_hostname, 32, 30, 48, colors['magenta'])

    # Shutdown button
    matrix.append([410, 20, 60, 60, '0'])
    icon = pygame.image.load("imgs/shutdown-icon-33.png")
    icon = pygame.transform.scale(icon, (60, 60))
    screen.blit(icon, [410, 20])

    # Printing measurement data
    if not DARWIN:
        print_measure_data(screen)

    matrix.append([30, 90, 80, 80, 'netinfo'])
    icon = pygame.image.load("imgs/net.png")
    icon = pygame.transform.scale(icon, (80, 80))
    screen.blit(icon, [30, 90])

    matrix.append([120, 90, 80, 80, 'xwin'])
    icon = pygame.image.load("imgs/xwin.png")
    icon = pygame.transform.scale(icon, (80, 80))
    screen.blit(icon, [120, 90])

    matrix.append([210, 90, 80, 80, 'shell'])
    icon = pygame.image.load("imgs/shell.png")
    icon = pygame.transform.scale(icon, (80, 80))
    screen.blit(icon, [210, 90])

    matrix.append([300, 90, 80, 80, 'services'])
    icon = pygame.image.load("imgs/servers.png")
    icon = pygame.transform.scale(icon, (80, 80))
    screen.blit(icon, [300, 90])

    matrix.append([30, 180, 80, 80, 'metasploit'])
    icon = pygame.image.load("imgs/metasploit.png")
    icon = pygame.transform.scale(icon, (80, 80))
    screen.blit(icon, [30, 180])

    matrix.append([120, 180, 80, 80, 'nmap'])
    icon = pygame.image.load("imgs/nmap_logo.png")
    icon = pygame.transform.scale(icon, (80, 80))
    screen.blit(icon, [120, 180])


def print_menu_net(screen, matrix,ipversion):
    # Background Color
    screen.fill(colors['black'])
    # Matrix is a mutable object, but if we assign to a value, Python will
    # create a new object. We need to use "functions" to change its value
    # matrix = [] -> This will not work
    del matrix[:]

    matrix.append([10, 10, 80, 80, 'menu1'])
    icon = pygame.image.load("imgs/back.png")
    icon = pygame.transform.scale(icon, (80, 80))
    screen.blit(icon, [10, 10])

    matrix.append([390, 10, 80, 60, 'netinfo_refresh_ip'])
    icon = pygame.image.load("imgs/ipv4ipv6.png")
    icon = pygame.transform.scale(icon, (80, 60))
    screen.blit(icon, [390, 10])

    matrix.append([390, 80, 60, 70, 'netinfo_wifi'])
    icon = pygame.image.load("imgs/wifi.png")
    icon = pygame.transform.scale(icon, (60, 70))
    screen.blit(icon, [390, 80])

    matrix.append([390, 160, 60, 70, 'netinfo_kismet'])
    icon = pygame.image.load("imgs/kismet.png")
    icon = pygame.transform.scale(icon, (60, 70))
    screen.blit(icon, [390, 160])

    matrix.append([390, 240, 60, 70, 'netinfo_sdr'])
    icon = pygame.image.load("imgs/sdr.png")
    icon = pygame.transform.scale(icon, (60, 60))
    screen.blit(icon, [390, 240])


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
                draw_label(screen, "Int: " + str(line[1]), 30, hzn, 24, colors['yellow'])
                hzn += 30
            else:
                if "inet6" in line and ipversion == 'IPv6':
                    line = line.split()
                    draw_label(screen, "IPv6: " + str(line[1]), 30, hzn, 24, colors['yellow'])
                    hzn += 30
                elif not ("inet6" in line) and ipversion == 'IPv4':
                    line = line.split()
                    draw_label(screen, "IPv4: " + str(line[1]), 30, hzn, 24, colors['yellow'])
                    hzn += 30


def print_menu_services(screen, matrix, service_matrix, page):
    pikali_services.check_service(service_matrix)

    # Background Color
    screen.fill(colors['black'])
    # Matrix is a mutable object, but if we assign to a value, Python will
    # create a new object. We need to use "functions" to change its value
    # matrix = [] -> This will not work
    del matrix[:]

    if page == 1:
        service_s = 'Hostapd'
    elif page == 2:
        service_s = 'Openvas'
    matrix.append([5, 10, 200, 60, 'services_' + service_s.lower()])
    iconf = "imgs/" + service_s + ".png"
    iconf = iconf.lower()
    icon = pygame.image.load(iconf)
    icon = pygame.transform.scale(icon, (60, 60))
    screen.blit(icon, [5, 10])
    if service_matrix[service_s.lower()] == 'on':
        draw_label(screen, service_s, 70, 30, 32, colors['green'])
        icon = pygame.image.load("imgs/swon.png")
        icon = pygame.transform.scale(icon, (40, 20))
    else:
        draw_label(screen, service_s, 70, 30, 32, colors['red'])
        icon = pygame.image.load("imgs/swoff.png")
        icon = pygame.transform.scale(icon, (40, 20))
    screen.blit(icon, [180, 30])

    if page == 1:
        service_s = 'Apache'
    elif page == 2:
        service_s = 'Snort'
    matrix.append([5, 130, 200, 60, 'services_' + service_s.lower()])
    iconf = "imgs/" + service_s + ".png"
    iconf = iconf.lower()
    icon = pygame.image.load(iconf)
    icon = pygame.transform.scale(icon, (60, 60))
    screen.blit(icon, [5, 130])
    if service_matrix[service_s.lower()] == 'on':
        draw_label(screen, service_s, 70, 150, 32, colors['green'])
        icon = pygame.image.load("imgs/swon.png")
        icon = pygame.transform.scale(icon, (40, 20))
    else:
        draw_label(screen, service_s, 70, 150, 32, colors['red'])
        icon = pygame.image.load("imgs/swoff.png")
        icon = pygame.transform.scale(icon, (40, 20))
    screen.blit(icon, [180, 150])

    if page == 1:
        service_s = 'PureFTP'
        matrix.append([240, 10, 200, 60, 'services_' + service_s.lower()])
        iconf = "imgs/" + service_s + ".png"
        iconf = iconf.lower()
        icon = pygame.image.load(iconf)
        icon = pygame.transform.scale(icon, (60, 60))
        screen.blit(icon, [240, 10])
        if service_matrix[service_s.lower()] == 'on':
            draw_label(screen, service_s, 305, 30, 32, colors['green'])
            icon = pygame.image.load("imgs/swon.png")
            icon = pygame.transform.scale(icon, (40, 20))
        else:
            draw_label(screen, service_s, 305, 30, 32, colors['red'])
            icon = pygame.image.load("imgs/swoff.png")
            icon = pygame.transform.scale(icon, (40, 20))
        screen.blit(icon, [415, 30])

    if page == 1:
        service_s = 'VNC'
        matrix.append([240, 130, 200, 60, 'services_' + service_s.lower()])
        iconf = "imgs/" + service_s + ".png"
        iconf = iconf.lower()
        icon = pygame.image.load(iconf)
        icon = pygame.transform.scale(icon, (60, 60))
        screen.blit(icon, [240, 130])
        if service_matrix['vnc'] == 'on':
            draw_label(screen, service_s, 305, 150, 32, colors['green'])
            icon = pygame.image.load("imgs/swon.png")
            icon = pygame.transform.scale(icon, (40, 20))
        else:
            draw_label(screen, service_s, 305, 150, 32, colors['red'])
            icon = pygame.image.load("imgs/swoff.png")
            icon = pygame.transform.scale(icon, (40, 20))
        screen.blit(icon, [415, 150])

    # Arrows
    if page == 1:
        matrix.append([5, 250, 70, 70, 'menu1'])
    elif page == 2:
        matrix.append([5, 250, 70, 70, 'services'])
    icon = pygame.image.load("imgs/back.png")
    icon = pygame.transform.scale(icon, (70, 70))
    screen.blit(icon, [5, 250])

    matrix.append([205, 250, 70, 70, 'menu1'])
    icon = pygame.image.load("imgs/top.png")
    icon = pygame.transform.scale(icon, (70, 70))
    screen.blit(icon, [205, 250])

    if page == 1:
        matrix.append([410, 250, 70, 70, 'services2'])
        icon = pygame.image.load("imgs/next.png")
        icon = pygame.transform.scale(icon, (70, 70))
        screen.blit(icon, [410, 250])


def print_menu_wifi(screen, matrix):
    # Background Color
    screen.fill(colors['black'])
    # Matrix is a mutable object, but if we assign to a value, Python will
    # create a new object. We need to use "functions" to change its value
    # matrix = [] -> This will not work
    del matrix[:]

    matrix.append([10, 10, 80, 80, 'netinfo'])
    icon = pygame.image.load("imgs/back.png")
    icon = pygame.transform.scale(icon, (80, 80))
    screen.blit(icon, [10, 10])

    matrix.append([120, 120, 80, 80, 'netinfo_wlan0'])
    icon = pygame.image.load("imgs/wifi.png")
    icon = pygame.transform.scale(icon, (80, 80))
    screen.blit(icon, [120, 120])
    draw_label(screen, 'wlan0', 125, 210, 32, colors['green'])

    matrix.append([320, 120, 80, 80, 'netinfo_wlan1'])
    icon = pygame.image.load("imgs/wifi.png")
    icon = pygame.transform.scale(icon, (80, 80))
    screen.blit(icon, [320, 120])
    draw_label(screen, 'wlan1', 325, 210, 32, colors['green'])


def print_menu_wifi_wlan(screen, matrix, wifi):
    # Background Color
    screen.fill(colors['black'])
    # Matrix is a mutable object, but if we assign to a value, Python will
    # create a new object. We need to use "functions" to change its value
    # matrix = [] -> This will not work
    del matrix[:]

    matrix.append([10, 10, 80, 80, 'netinfo_wifi'])
    icon = pygame.image.load("imgs/back.png")
    icon = pygame.transform.scale(icon, (80, 80))
    screen.blit(icon, [10, 10])

    matrix.append([390, 10, 80, 60, 'netinfo_' + wifi + '_config'])
    icon = pygame.image.load("imgs/config.png")
    icon = pygame.transform.scale(icon, (60, 60))
    screen.blit(icon, [390, 10])


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
        draw_label(screen, wlan, 30, hzn, 24, colors['yellow'])
        hzn += 30
        for k, v in data.iteritems():
            draw_label(screen, k + ': ' + v, 30, hzn, 24, colors['yellow'])
            hzn += 30

def print_menu_wifi_config(screen, matrix, wifi):
    # Background Color
    screen.fill(colors['black'])
    # Matrix is a mutable object, but if we assign to a value, Python will
    # create a new object. We need to use "functions" to change its value
    # matrix = [] -> This will not work
    del matrix[:]

    matrix.append([10, 10, 80, 80, 'netinfo_wifi'])
    icon = pygame.image.load("imgs/back.png")
    icon = pygame.transform.scale(icon, (80, 80))
    screen.blit(icon, [10, 10])

    essid = []
    # Printing IP
    if not DARWIN:
        command = 'iwlist ' + wifi + ' scanning'
        process = Popen(command, stdout=PIPE, shell=True)
        output = process.communicate()[0]
    else:
        output = 'Cell1\nESSID:"Test_1"\nCell2\nESSID:"Test_2y"\nCell3\nESSID:"Test3"\nCell4\nESSID:"Test4"\nCell5\nESSID:"Test5"\nCell6\nESSID:"Test6"\n'
    output = output.split("\n")
    for line in output:
        line = line.strip()
        if line.startswith('ESSID'):
            essid.append(line.split('"')[1])

    draw_selection_list(screen, matrix, essid, 10, 100, 250, colors['blue'])

