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

TEMPLMZFILE = os.getcwd()+'/jinja2temps/lmnewzone.conf'
TEMPLSZFILE = os.getcwd()+'/jinja2temps/lsnewzone.conf'
TEMPLDOMFILE = os.getcwd()+'/jinja2temps/lmdom.conf'

templmz = templateEnv.get_template( TEMPLMZFILE )
templsz = templateEnv.get_template( TEMPLSZFILE )
templdom = templateEnv.get_template( TEMPLDOMFILE )

env.roledefs = {
    'dns': [str(raw_input('Please enter NS1 IP address: ')), str(raw_input('Please enter NS2 IP address: '))]
}

env.user = raw_input('Please enter username for UNIX/Linux server: ')
env.password = getpass.getpass()

print('1. Please write domain name and click Enter button.')
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
                    tempmzVars = { "ns1" : env.roledefs['dns'][0], "ns2" : env.roledefs['dns'][1], "domain" : ent, }
                    outputmzText = tempmz.render( tempmzVars )
                    outputdomText = tempdom.render( tempmzVars )
                    if server == env.roledefs['dns'][0]:
                        with open("zone_"+env.roledefs['dns'][0]+".conf", "wb") as ns1zone:
                            ns1zone.write(outputmzText)
                        with open(ent+".zone", "wb") as masdom:
                            masdom.write(outputdomText)
                        print("This is NS1 "+env.roledefs['dns'][0]+" server")
                        put('zone_'+env.roledefs['dns'][0]+'.conf', '/usr/local/etc/namedb/')
                        put(ent+'.zone', '/usr/local/etc/namedb/master/')
                        run('cat /usr/local/etc/namedb/zone_'+env.roledefs['dns'][0]+'.conf >> /usr/local/etc/namedb/named.conf')
                        run('service named restart')

                def writeszone():
                    tempszVars = { "ns1" : env.roledefs['dns'][0], "domain" : ent, }
                    outputszText = tempsz.render( tempszVars )
                    if server == env.roledefs['dns'][1]:
                        with open("zone_"+env.roledefs['dns'][1]+".conf", "wb") as ns2zone:
                            ns2zone.write(outputszText)
                        print("This is NS2 "+env.roledefs['dns'][1]+" server")
                        put('zone_'+env.roledefs['dns'][1]+'.conf', '/usr/local/etc/namedb/')
                        run('cat /usr/local/etc/namedb/zone_'+env.roledefs['dns'][1]+'.conf >> /usr/local/etc/namedb/named.conf')
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
                    templmzVars = { "ns1" : env.roledefs['dns'][0], "ns2" : env.roledefs['dns'][1], "domain" : ent, }
                    outputlmzText = templmz.render( templmzVars )
                    outputldomText = templdom.render( templmzVars )
                    if server == env.roledefs['dns'][0]:
                        with open("zone_"+env.roledefs['dns'][0]+".conf", "wb") as ns1zone:
                            ns1zone.write(outputlmzText)
                        with open(ent+".zone", "wb") as masdom:
                            masdom.write(outputldomText)
                        print("This is NS1 "+env.roledefs['dns'][0]+" server")
                        put('zone_'+env.roledefs['dns'][0]+'.conf', '/etc/namedb/')
                        put(ent+'.zone', '/etc/namedb/master/')
                        run('cat /etc/namedb/zone_'+env.roledefs['dns'][0]+'.conf >> /etc/named.conf')
                        run('systemctl restart named.service')

                def writelszone():
                    templszVars = { "ns1" : env.roledefs['dns'][0], "domain" : ent, }
                    outputlszText = templsz.render( templszVars )
                    if server == env.roledefs['dns'][1]:
                        with open("zone_"+env.roledefs['dns'][1]+".conf", "wb") as ns2zone:
                            ns2zone.write(outputlszText)
                        print("This is NS2 "+env.roledefs['dns'][1]+" server")
                        put('zone_'+env.roledefs['dns'][1]+'.conf', '/etc/namedb/')
#                       print("File copied to NS2 -> "+env.roledefs['dns'][1]+" server")
                        run('cat /etc/namedb/zone_'+env.roledefs['dns'][1]+'.conf >> /etc/named.conf')
                        run('systemctl restart named.service')
 
                if ent != 2 and len(ent) > 4:
                    writelmzone()
                    writelszone()
                else:
                    print("\nMinimal symbol count must be 4.")
                    sys.exit()
        else:
            print("The script is not determine server type. For this reason you cannot use this script.")

