#!/usr/bin/env python2.7

import sys
import os
import jinja2

from fabric.api import *
from fabric.tasks import execute
import getpass

templateLoader = jinja2.FileSystemLoader( searchpath="/" )
templateEnv = jinja2.Environment( loader=templateLoader )
TEMPMZFILE = os.getcwd()+'/jinja2temps/fmnewzone.conf'
TEMPSZFILE = os.getcwd()+'/jinja2temps/fsnewzone.conf'
TEMPDOMFILE = os.getcwd()+'/jinja2temps/mszone.conf'

tempmz = templateEnv.get_template( TEMPMZFILE )
tempsz = templateEnv.get_template( TEMPSZFILE )
tempdom = templateEnv.get_template( TEMPDOMFILE )

env.roledefs = {
    'dns': [str(raw_input('Please enter NS1 IP address: ')), str(raw_input('Please enter NS2 IP address: '))]
}

env.user = raw_input('Please enter username for UNIX/Linux server: ')
env.password = getpass.getpass()

print('1. Please write domain name and click Enter button.')
print('2. For exit, write 2 and click Enter button: ')
ent = raw_input('Write your choose: ')

cbconf = '/etc/named.conf'
cbindpath = '/etc/namedb'
fbconf = '/usr/local/etc/namedb/named.conf'
fbindpath = '/usr/local/etc/namedb'
def domainchecker(conf):
    if server == env.roledefs['dns'][0]:
        fzonename = run('cat '+conf+' | grep '+ent+' |  head -1 | awk \'{ print $2 }\' | sed \'s/"//g\'')
        fzonefile = run('cat '+conf+' | grep '+ent+' |  tail -1 | awk \'{ print $2 }\' | sed \'s/"//g;s/;//g\' | awk -F/ \'{print $NF}\' | cut -f1,2 -d\'.\'')
        if ent == fzonename and fzonefile == ent:
            print(' Entered domain name '+ent+' already exists on the NS1 '+env.roledefs['dns'][0]+' server!!!')
            print(' If you want add new record for this '+ent+' domain name, please use ./python-add-record.py script.')
            sys.exit()
        else:
            pass

def writemzone(bindpath, conf):
    tempmzVars = { "ns1" : env.roledefs['dns'][0], "ns2" : env.roledefs['dns'][1], "domain" : ent, "bdpath" : bindpath }
    outputmzText = tempmz.render( tempmzVars )
    outputdomText = tempdom.render( tempmzVars )
    if server == env.roledefs['dns'][0]:
        with open("zone_"+env.roledefs['dns'][0]+".conf", "wb") as ns1zone:
            ns1zone.write(outputmzText)
        with open(ent+".zone", "wb") as masdom:
            masdom.write(outputdomText)
        print("This is NS1 "+env.roledefs['dns'][0]+" server")
        put('zone_'+env.roledefs['dns'][0]+'.conf', ''+bindpath+'')
        put(ent+'.zone', ''+bindpath+'/master/')
        run('cat '+bindpath+'/zone_'+env.roledefs['dns'][0]+'.conf >> '+conf+'')
        run('service named restart')

def writeszone(bindpath, conf):
    tempszVars = { "ns1" : env.roledefs['dns'][0], "domain" : ent, "bdpath" : bindpath}
    outputszText = tempsz.render( tempszVars )
    if server == env.roledefs['dns'][1]:
        with open("zone_"+env.roledefs['dns'][1]+".conf", "wb") as ns2zone:
            ns2zone.write(outputszText)
        print("This is NS2 "+env.roledefs['dns'][1]+" server")
        put('zone_'+env.roledefs['dns'][1]+'.conf', ''+bindpath+'')
        #print("File copied to NS2 -> "+env.roledefs['dns'][1]+" server")
        run('cat '+bindpath+'/zone_'+env.roledefs['dns'][1]+'.conf >> '+conf+'')
        run('service named restart')

def checkservice():
    print(' DNS service is not working!!!')
    print(' To install DNS bind please use, ./python-ms-sl-dns.py script. ')
    sys.exit()

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
            bindfpidfile = run('cat /var/run/named/pid')
            bindfpid = run('ps waux | grep named | grep -v grep | awk \'{ print $2 }\'')
            if getfbindpack == '/usr/local/sbin/named' and bindfpid == bindfpidfile:
                domainchecker(fbconf)

                if ent != 2 and len(ent) > 4:
                    writemzone(fbindpath, fbconf)
                    writeszone(fbindpath, fbconf)
                else:
                    print("\nMinimal symbol count must be 4.")
                    sys.exit()
            else:
                checkservice()

        elif osver == 'Linux' and lintype == 'CentOS':
            getlbindpack = run('which named')
            bindlpidfile = run('cat /var/run/named/named.pid')
            bindlpid = run('ps waux|grep named | grep -v grep | awk \'{ print $2 }\'')
            if getlbindpack == '/usr/sbin/named' and bindlpidfile == bindlpid:
                domainchecker(cbconf)
                if ent != 2 and len(ent) > 4:
                    writemzone(cbindpath, cbconf)
                    writeszone(cbindpath, cbconf)
                else:
                    print("\nMinimal symbol count must be 4.")
                    sys.exit()
            else:
                checkservice()
        else:
            print("The script is not determine server type. For this reason you cannot use this script.")
