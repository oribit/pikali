import sys
import pikali_bag
from subprocess import Popen, PIPE

def init_services(service_matrix):
    service_matrix['hostapd'] = 'off'
    service_matrix['apache'] = 'off'
    service_matrix['pureftp'] = 'off'
    service_matrix['vnc'] = 'off'
    service_matrix['openvas'] = 'off'
    service_matrix['snort'] = 'off'
    service_matrix['mysql'] = 'off'

def check_service(service_matrix, service='all'):
    # hostapd
    if service == 'hostapd' or service == 'all':
        command = 'service hostapd status'
        process = Popen(command.split(), stdout=PIPE)
        output = process.communicate()[0]
        if 'active: active (running)' in output.lower() and not 'active: inactive (dead)' in output.lower():
            service_matrix['hostapd'] = 'on'
        else:
            service_matrix['hostapd'] = 'off'
    # Apache
    if service == 'apache' or service == 'all':
        command = '/usr/sbin/service apache2 status'
        process = Popen(command.split(), stdout=PIPE)
        output = process.communicate()[0]
        if 'active: active (running)' in output.lower() and not 'active: inactive (dead)' in output.lower():
            service_matrix['apache'] = 'on'
        else:
            service_matrix['apache'] = 'off'

    # FTP
    if service == 'pureftp' or service == 'all':
        command = 'service pure-ftpd status'
        process = Popen(command.split(), stdout=PIPE)
        output = process.communicate()[0]
        if 'active: active (running)' in output.lower() and not 'active: inactive (dead)' in output.lower():
            service_matrix['pureftp'] = 'on'
        else:
            service_matrix['pureftp'] = 'off'

    # VNC-Server
    if service == 'vnc' or service == 'all':
        command = 'ps -ef | grep vnc'
        process = Popen(command, stdout=PIPE, shell=True)
        output = process.communicate()[0]
        if 'vnc :1' in output.lower():
            service_matrix['vnc'] = 'on'
        else:
            service_matrix['vnc'] = 'off'

def start_service_vnc():
    pikali_bag.run_cmd("/usr/bin/vncserver :1")

def stop_service_vnc():
    pikali_bag.run_cmd("/usr/bin/vncserver -kill :1")

def start_service_apache():
    pikali_bag.run_cmd("/usr/sbin/service apache2 start")

def stop_service_apache():
    pikali_bag.run_cmd("/usr/sbin/service apache2 stop")

def start_service_pureftp():
    pikali_bag.run_cmd("/usr/sbin/service pure-ftpd start")

def stop_service_pureftp():
    pikali_bag.run_cmd("/usr/sbin/service pure-ftpd stop")
