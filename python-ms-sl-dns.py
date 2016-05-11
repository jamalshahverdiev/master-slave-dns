#!/usr/bin/env python2.7

import sys
import os
import jinja2

from fabric.api import *
from fabric.tasks import execute
import getpass

templateLoader = jinja2.FileSystemLoader( searchpath="/" )
templateEnv = jinja2.Environment( loader=templateLoader )
TEMPMFILE = os.getcwd()+'/jinja2temps/fmnamed.conf'
TEMPSFILE = os.getcwd()+'/jinja2temps/fsnamed.conf'
TEMPLMFILE = os.getcwd()+'/jinja2temps/lmnamed.conf'
TEMPLSFILE = os.getcwd()+'/jinja2temps/lsnamed.conf'

tempm = templateEnv.get_template( TEMPMFILE )
temps = templateEnv.get_template( TEMPSFILE )
templm = templateEnv.get_template( TEMPLMFILE )
templs = templateEnv.get_template( TEMPLSFILE )
env.roledefs = {
    'dns': [str(raw_input('Please enter NS1 IP address: ')), str(raw_input('Please enter NS2 IP address: '))]
}

tempmVars = { "ns1" : env.roledefs['dns'][0], "ns2" : env.roledefs['dns'][1] }

outputmText = tempm.render( tempmVars )
outputsText = temps.render( tempmVars )
outputlmText = templm.render( tempmVars )
outputlsText = templs.render( tempmVars )

env.user = raw_input('Please enter username for UNIX/Linux server: ')
env.password = getpass.getpass()

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
            bindpidfile = run('cat /var/run/named/pid')
            bindpid = run('ps waux|grep bind | grep -v grep | awk \'{ print $2 }\'')
            if getfbindpack == '/usr/local/sbin/named' and bindpidfile == bindpid:
                print(' You have already installed and running bind...')
                print(' If you want add new domain, please use ./python-add-zone.py script. ')
                sys.exit()
            elif getfbindpack != '/usr/local/sbin/named':
                run('pkg install -y bind910')
                run('echo named_enable="YES" >> /etc/rc.conf')
                if server == env.roledefs['dns'][0]:
                    print("Master DNS is installed and configured on NS1 server")
                    with open("named_"+env.roledefs['dns'][0]+".conf", "wb") as ns1file:
                        ns1file.write(outputmText)
                    put('named_'+env.roledefs['dns'][0]+'.conf', '/usr/local/etc/namedb/named.conf')
                elif server == env.roledefs['dns'][1]:
                    print("Slave DNS is installed and configured on NS2 server")
                    with open("named_"+env.roledefs['dns'][1]+".conf", "wb") as ns2file:
                        ns2file.write(outputsText)
                    put('named_'+env.roledefs['dns'][1]+'.conf', '/usr/local/etc/namedb/named.conf')
                run('mkdir /var/log/bind/')
                run('touch /var/log/bind/named.log /var/log/bind/query.log')
                run('chown -R bind:bind /var/log/bind/')
                run('/usr/local/etc/rc.d/named start')
            print("This was FreeBSD server")
        elif osver == 'Linux' and lintype == 'CentOS':
            getlbindpack = run('which named')
            bindlpidfile = run('cat /var/run/named/named.pid')
            bindlpid = run('ps waux|grep named | grep -v grep | awk \'{ print $2 }\'')
            if getlbindpack == '/usr/sbin/named' and bindlpidfile == bindlpid:
                print(' You have already installed and running bind...')
                print(' If you want add new domain, please use ./python-add-zone.py script. ')
                sys.exit()
            elif getlbindpack != '/usr/sbin/named':
                run('yum -y install bind bind-utils bind-chroot')
                run('systemctl start named')
                run('systemctl enable named')
                if server == env.roledefs['dns'][0]:
                    print("Master DNS is installed and configured on NS1 server")
                    with open("lnamed_"+env.roledefs['dns'][0]+".conf", "wb") as ns1file:
                        ns1file.write(outputlmText)
                    put('lnamed_'+env.roledefs['dns'][0]+'.conf', '/etc/named.conf')
                elif server == env.roledefs['dns'][1]:
                    print("Slave DNS is installed and configured on NS2 server")
                    with open("lnamed_"+env.roledefs['dns'][1]+".conf", "wb") as ns2file:
                        ns2file.write(outputlsText)
                    put('lnamed_'+env.roledefs['dns'][1]+'.conf', '/etc/named.conf')
                run('mkdir -p /var/log/bind/ /etc/namedb/{master,slave}')
                run('touch /var/log/bind/named.log /var/log/bind/query.log')
                run('chown -R named:named /var/log/bind/ /etc/namedb/{master,slave}')
                run('systemctl restart named')
            print("This was CentOS server")
        else:
            print("The script is not determine server type. For this reason you cannot use this script.")
