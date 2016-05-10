#!/usr/bin/env python3.4

from netmiko import *

#input('Please enter NS1 IP address: '), input('Please enter NS2 IP address: ')

ns1ip = input('Please enter NS1 IP address: ')
ns1rpass = input('Please enter NS1 root user password: ')
ns1 = {
        'device_type': 'linux',
        'ip': ns1ip,
        'username': 'root',
        'password': ns1rpass,
        'port' : 22,
        }

ns1_connect = ConnectHandler(**ns1)

output = ns1_connect.send_command("ifconfig")
print(output)

ns2ip = input('Please enter NS2 IP address: ')
ns2rpass = input('Please enter NS2 root user password: ')
ns2 = {
        'device_type': 'ovs_linux',
        'ip': ns2ip,
        'username': 'root',
        'password': ns2rpass,
        'port' : 22, # optional, defaults to 22
        }

ns2_connect = ConnectHandler(**ns2)

ns2_output = ns2_connect.send_command("ifconfig")
print(ns2_output)
