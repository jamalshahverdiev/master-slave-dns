#!/usr/bin/env python2.7

import sys
import os
import jinja2

from fabric.api import *
from fabric.tasks import execute
import getpass

templateLoader = jinja2.FileSystemLoader( searchpath="/" )
templateEnv = jinja2.Environment( loader=templateLoader )
TEMPDOMFILE = os.getcwd()+'/jinja2temps/mszone.conf'

tempdom = templateEnv.get_template( TEMPDOMFILE )

TEMPLDOMFILE = os.getcwd()+'/jinja2temps/lmdom.conf'

templdom = templateEnv.get_template( TEMPLDOMFILE )

env.roledefs = {
    'dns': [str(raw_input('Please enter NS1 IP address: ')), str(raw_input('Please enter NS2 IP address: '))]
}

env.user = raw_input('Please enter username for UNIX/Linux server: ')
env.password = getpass.getpass()

print('1. Write domain name which you want to update: ')
print('2. For exit, write 2 and click Enter button: ')
ent = raw_input('Write your choose: ')

for server in env.roledefs['dns']:
    env.host_string = server
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'),
        warn_only=True
    ):
        osver = run('uname -s')
        lintype = run('cat /etc/redhat-release | awk \'{ print $1 }\'')
        ftype = run('uname -v | awk \'{ print $2 }\' | cut -f1 -d \'.\'')
        if osver == 'FreeBSD' and ftype >= 10:
            getfbindpack = run('which named')
            if getfbindpack == '/usr/local/sbin/named':
                def writemzone():
                    if server == env.roledefs['dns'][0]:
                        fzonename = run('cat /usr/local/etc/namedb/named.conf | grep '+ent+' |  head -1 | awk \'{ print $2 }\' | sed \'s/"//g\'')
                        fzonefile = run('cat /usr/local/etc/namedb/named.conf | grep '+ent+' |  tail -1 | awk \'{ print $2 }\' | sed \'s/"//g;s/;//g\' | cut -f 7 -d\'/\' | cut -f1,2 -d \'.\'')
                        if ent == fzonename and fzonefile == ent:
                            print("This domain name really exists...")
                            print("""Please choose record type which you want to create: 
                                    A
                                    NS
                                    MX
                                    TXT
                                    SRV
                                    """)
                            rec = raw_input('Write your choose record type and press the enter button: ')
                            if rec == "A":
                                recnameA = raw_input('Please enter A record name: ')
                                ipforA = raw_input('Enter IP address for A record: ')
                                print('evvel')
                                run('ifconfig')
                                print('sonra')
                                #run('echo "'+recnameA+'            IN  A   '+ipforA+'" >> /usr/local/etc/named/master/'+ent+'.zone')
                        else:
                            print("Entered domain name is not exits and you cannot add new record.")
                            print("Please use ./python-add-zone.py script for add new nomain.")

                def writeszone():
                    if server == env.roledefs['dns'][1]:
                        run('service named restart')

                if ent != 2 and len(ent) > 4:
                    writemzone()
                    writeszone()
                else:
                    print("\nMinimal symbol count must be 4.")
                    sys.exit()
        elif osver == 'Linux' and lintype == 'CentOS':
            getlbindpack = run('which named')
            bindlpidfile = run('cat /var/run/named/named.pid')
            bindlpid = run('ps waux|grep named | grep -v grep | awk \'{ print $2 }\'')
            if getlbindpack == '/usr/sbin/named' and bindlpidfile == bindlpid:
                def writelmzone():
                    if server == env.roledefs['dns'][0]:
                        a = 5
                        b = 6
                        print(a+b)
                def writelszone():
                    if server == env.roledefs['dns'][1]:
                        a = 6 
                        b = 7
                        print(a+b)
                if ent != 2 and len(ent) > 4:
                    writelmzone()
                    writelszone()
                else:
                    print("\nMinimal symbol count must be 4.")
                    sys.exit()
        else:
            print("The script is not determine server type. For this reason you cannot use this script.")

