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
    make_label(screen, temp, 210, 20, 32, colors['orange'])


# define function for printing text in a specific place with a specific width and height with a specific colour and border
def make_button(screen, text, xpo, ypo, width, height, colour):
    pygame.draw.rect(screen, colour, (xpo-10,ypo-10,width,height),3)
    pygame.draw.rect(screen, colour, (xpo-9,ypo-9,width-1,height-1),1)
    pygame.draw.rect(screen, colour, (xpo-8,ypo-8,width-2,height-2),1)
    font=pygame.font.Font(None,42)
    label=font.render(str(text), 1, (colour))
    screen.blit(label,(xpo,ypo))


# define function for printing text in a specific place with a specific colour
def make_label(screen, text, xpo, ypo, fontsize, colour):
    font=pygame.font.Font(None,fontsize)
    label=font.render(str(text), 1, (colour))
    screen.blit(label,(xpo,ypo))


def print_menu1(screen, matrix, pi_hostname):
    # Background Color
    screen.fill(colors['black'])

    # Matrix is a mutable object, but if we assign to a value, Python will
    # create a new object. We need to use "functions" to change its value
    # matrix = [] -> This will not work
    del matrix[:]

    # Printing hostname
    make_label(screen, pi_hostname, 32, 30, 48, colors['magenta'])

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

    matrix.append([390, 80, 60, 70, 'menu_wifi'])
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
                make_label(screen, "Int: " + str(line[1]), 30, hzn, 24, colors['yellow'])
                hzn += 30
            else:
                if "inet6" in line and ipversion == 'IPv6':
                    line = line.split()
                    make_label(screen, "IPv6: " + str(line[1]), 30, hzn, 24, colors['yellow'])
                    hzn += 30
                elif not ("inet6" in line) and ipversion == 'IPv4':
                    line = line.split()
                    make_label(screen, "IPv4: " + str(line[1]), 30, hzn, 24, colors['yellow'])
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
        make_label(screen, service_s, 70, 30, 32, colors['green'])
        icon = pygame.image.load("imgs/swon.png")
        icon = pygame.transform.scale(icon, (40, 20))
    else:
        make_label(screen, service_s, 70, 30, 32, colors['red'])
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
        make_label(screen, service_s, 70, 150, 32, colors['green'])
        icon = pygame.image.load("imgs/swon.png")
        icon = pygame.transform.scale(icon, (40, 20))
    else:
        make_label(screen, service_s, 70, 150, 32, colors['red'])
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
            make_label(screen, service_s, 305, 30, 32, colors['green'])
            icon = pygame.image.load("imgs/swon.png")
            icon = pygame.transform.scale(icon, (40, 20))
        else:
            make_label(screen, service_s, 305, 30, 32, colors['red'])
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
            make_label(screen, service_s, 305, 150, 32, colors['green'])
            icon = pygame.image.load("imgs/swon.png")
            icon = pygame.transform.scale(icon, (40, 20))
        else:
            make_label(screen, service_s, 305, 150, 32, colors['red'])
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
    '''
    matrix.append([390, 10, 80, 60, 'netinfo_refresh_ip'])
    icon = pygame.image.load("imgs/ipv4ipv6.png")
    icon = pygame.transform.scale(icon, (80, 60))
    screen.blit(icon, [390, 10])

    matrix.append([390, 80, 60, 70, 'wifi_menu'])
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
    '''

    # Printing IP
    command = 'iwconfig wlan0; iwconfig wlan1'

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
            wlan_d[wlan]['mac_ap'] = ''.join([x for x in t_line if x.startswith('Access')]).split(':')[1]

    for wlan, data in wlan_d.iteritems():
        make_label(screen, wlan, 30, hzn, 24, colors['yellow'])
        for k, v in data.iteritems():
            make_label(screen, k + ': ' + v, 30, hzn, 24, colors['yellow'])
            hzn += 30
