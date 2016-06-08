#!/usr/bin/env python2.7

import sys
import os
#import logging
#logging.basicConfig(level=logging.DEBUG)

from fabric.api import *
from fabric.tasks import execute
import getpass

env.roledefs = {
    'dns': [str(raw_input('Please enter NS1 IP address: ')), str(raw_input('Please enter NS2 IP address: '))]
}

if env.roledefs['dns'][0] == env.roledefs['dns'][1]:
    print('NS1 server IP address cannot be the same as NS2 server IP address.')
    print('Please write careful and try again...')
    sys.exit()
elif env.roledefs['dns'][0] == "" and env.roledefs['dns'][1]:
    print('Input for NS1 server IP address cannot be empty.')
    sys.exit()
elif env.roledefs['dns'][0] and env.roledefs['dns'][1] == "":
    print('Input for NS2 server IP address cannot be empty.')
    sys.exit()
elif env.roledefs['dns'][0] == "" and env.roledefs['dns'][1] == "":
    print('Input for NS1 and NS2 server IP address cannot be empty.')
    sys.exit()

def serialReplacer():
    serforZone = local('cat ./recfold/'+ent+'.zone | grep Serial | awk \'{ print $1 }\'', capture=True)
    reps = {str(serforZone):str(int(serforZone)+1)}
    with open(os.getcwd()+'/recfold/'+ent+'1.zone', 'w') as outfile:
        with open(os.getcwd()+'/recfold/'+ent+'.zone', 'r') as infile:
            for line in infile:
                for src, target in reps.iteritems():
                    line = line.replace(src, target)
                outfile.write(line)

cbindpath = '/etc/namedb'
fbindpath = '/usr/local/etc/namedb'
def addArec(bindpath):
    get(bindpath+'/master/'+ent+'.zone', os.getcwd()+'/recfold/')
    recnameA = raw_input('Please enter A record name(For example: "web", "share" ): ')
    ipforA = raw_input('Enter IP address for A record: ')
    local('echo \"'+recnameA+'\t\tIN  A   '+ipforA+'\" >> '+os.getcwd()+'/recfold/'+ent+'.zone')
    serforZone = local('cat ./recfold/'+ent+'.zone | grep Serial | awk \'{ print $1 }\'', capture=True)
    serialReplacer()
    put(os.getcwd()+'/recfold/'+ent+'1.zone', bindpath+'/master/'+ent+'.zone')
    run('service named restart')

def addNSrec(bindpath):
    get(bindpath+'/master/'+ent+'.zone', os.getcwd()+'/recfold/')
    recnameNS = raw_input('Please enter NS record name(For example: ns1.example.com. ): ')
    local('echo \"@\t\tIN  NS  '+recnameNS+'\" >> '+os.getcwd()+'/recfold/'+ent+'.zone')
    serialReplacer()
    put(os.getcwd()+'/recfold/'+ent+'1.zone', bindpath+'/master/'+ent+'.zone')
    run('service named restart')
    print("You added NS record but, each NS needs one A record. Please add A record for this NS.")
    addArec(bindpath)

def addMXrec(bindpath):
    get(bindpath+'/master/'+ent+'.zone', os.getcwd()+'/recfold/')
    recnameMX = raw_input('Please enter MX record name(For example: newmail.example.com. ): ')
    MXprio = raw_input('Please enter MX priority number: ')
    local('echo \"@\t\tIN  MX  '+MXprio+'   '+recnameMX+'\" >> '+os.getcwd()+'/recfold/'+ent+'.zone')
    serialReplacer()
    put(os.getcwd()+'/recfold/'+ent+'1.zone', bindpath+'/master/'+ent+'.zone')
    run('service named restart')
    print("You added MX record but, each MX needs one A record. Please add A record for this MX.")
    addArec(bindpath)

def addTXTrec(bindpath):
    get(bindpath+'/master/'+ent+'.zone', os.getcwd()+'/recfold/')
    recnameTXT = raw_input('Please enter TXT record name(For example example.com. ): ')
    PTRip = raw_input('Please enter PTR IP address for this TXT record: ')
    local('echo \''+ent+'.\tIN  TXT \"v=spf1 +a +mx +ptr ip4:'+PTRip+' -all\"\' >> '+os.getcwd()+'/recfold/'+ent+'.zone')
    #os.system('echo \''+ent+'.\t\tIN  TXT \"v=spf1 +a +mx +ptr ip4:'+PTRip+' -all"\' >> '+os.getcwd()+'/recfold/'+ent+'.zone')
    serialReplacer()
    put(os.getcwd()+'/recfold/'+ent+'1.zone', bindpath+'/master/'+ent+'.zone')
    run('service named restart')

def addSRVrec(bindpath):
    get(bindpath+'/master/'+ent+'.zone', os.getcwd()+'/recfold/')
    srvInputs()
    output = local('echo \"'+srvname+'.'+prtcol+'.'+bdname+'.\tIN\tSRV\t'+prori+'   '+weight+'   '+portnum+'    '+recnameSRV+'.\" >> '+os.getcwd()+'/recfold/'+ent+'.zone')
    serialReplacer()
    put(os.getcwd()+'/recfold/'+ent+'1.zone', bindpath+'/master/'+ent+'.zone')
    print('You must add A record for this '+recnameSRV+' FQDN.')
    addArec(bindpath)
    run('service named restart')

def recPrint():
    print("This domain name really exists...")
    print("""Please choose record type which you want to create: 
            A
            NS
            MX
            TXT
            SRV
            """)

def writeszone():
    if server == env.roledefs['dns'][1]:
        run('service named restart')

def srvInputs():
    global recnameSRV
    recnameSRV = raw_input('Please enter FQDN for SRV record name(For example: jabber.example.com): ')
    global srvname 
    srvname = raw_input('Please enter service name for this SRV record(For example: _http, _ftp, _ldap): ')
    global prtcol
    prtcol = raw_input('Please enter protocol for this SRV record(For example: _tcp, _udp): ')
    global bdname
    bdname = raw_input('Please enter base domain name for this SRV record(For example: example.com): ')
    global prori
    prori = raw_input('Please enter priority for this SRV record(For example: 0-65535, Lowest is highest priority): ')
    global weight
    weight = raw_input('Please enter wight for this SRV record(For example: 0-65535, highest is most frequently delivered): ')
    global portnum
    portnum = raw_input('Please enter port number for this SRV record(For example: 80 for _http service): ')

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
                            recPrint()
                            rec = raw_input('Write record type and press the enter button: ')
                            if rec == "A":
                                addArec(fbindpath)
                            elif rec == "NS":
                                addNSrec(fbindpath)
                            elif rec == "MX":
                                addMXrec(fbindpath)
                            elif rec == "TXT":
                                addTXTrec(fbindpath)
                            elif rec == "SRV":
                                addSRVrec(fbindpath)
                            else:
                                print("This script only supports A, NS, MX, TXT and SRV record types.")
                        else:
                            print("Entered domain name is not exits and you cannot add new record.")
                            print("Please use ./python-add-zone.py script for add new nomain.")

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
                        fzonename = run('cat /etc/named.conf | grep '+ent+' |  head -1 | awk \'{ print $2 }\' | sed \'s/"//g\'')
                        fzonefile = run('cat /etc/named.conf | grep '+ent+' |  tail -1 | awk \'{ print $2 }\' | sed \'s/"//g;s/;//g\' | cut -f 5 -d\'/\' | cut -f1,2 -d \'.\'')
                        if ent == fzonename and fzonefile == ent:
                            recPrint()
                            rec = raw_input('Write record type and press the enter button: ')
                            if rec == "A":
                                addArec(cbindpath)
                            elif rec == "NS":
                                addNSrec(cbindpath)
                            elif rec == "MX":
                                addMXrec(cbindpath)
                            elif rec == "TXT":
                                addTXTrec(cbindpath)
                            elif rec == "SRV":
                                addSRVrec(cbindpath)
                            else:
                                print("This script only supports A, NS, MX, TXT and SRV record types.")
                        else:
                            print("Entered domain name is not exits and you cannot add new record.")
                            print("Please use ./python-add-zone.py script for add new nomain.")

                if ent != 2 and len(ent) > 4:
                    writelmzone()
                    writeszone()
                else:
                    print("\nMinimal symbol count must be 4.")
                    sys.exit()

        else:
            print("The script is not determine server type. For this reason you cannot use this script.")
