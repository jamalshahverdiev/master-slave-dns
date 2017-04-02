#!/usr/bin/env python2.7
import sys
import os
#import logging
#logging.basicConfig(level=logging.DEBUG)
sys.path.insert(0, './lib')
from mslsvars import *
from fabric.api import *
from fabric.tasks import execute
import getpass

env.roledefs = {
    'dns': [str(raw_input(''+enter+' NS1 '+ipadd+': ')), str(raw_input(''+enter+' NS2 '+ipadd+': '))]
}

if env.roledefs['dns'][0] == env.roledefs['dns'][1]:
    print('NS1 '+nserver+' '+ipadd+' cannot be the same as NS2 '+nserver+' '+ipadd+'.')
    print('Please write careful and try again...')
    sys.exit()
elif env.roledefs['dns'][0] == "" and env.roledefs['dns'][1]:
    print('Input for NS1 '+nserver+' '+ipadd+' cannot be empty.')
    sys.exit()
elif env.roledefs['dns'][0] and env.roledefs['dns'][1] == "":
    print('Input for NS2 '+nserver+' '+ipadd+' cannot be empty.')
    sys.exit()
elif env.roledefs['dns'][0] == "" and env.roledefs['dns'][1] == "":
    print('Input for NS1 and NS2 '+nserver+' '+ipadd+' cannot be empty.')
    sys.exit()

def serialReplacer():
    serforZone = local('cat ./recfold/'+ent+'.zone | grep Serial | awk \'{ print $1 }\'', capture=True)
    reps = { str(serforZone):str(int(serforZone) + int(1)) }
    with open(os.getcwd()+'/recfold/'+ent+'1.zone', 'w') as outfile:
        with open(os.getcwd()+'/recfold/'+ent+'.zone', 'r') as infile:
            for line in infile:
                for src, target in reps.iteritems():
                    line = line.replace(src, target)
                outfile.write(line)

def addArec(bindpath):
    get(bindpath+'/master/'+ent+'.zone', os.getcwd()+'/recfold/')
    recnameA = raw_input(''+enter+' '+a+' name(For example: "web", "share" ): ')
    ipforA = raw_input(''+enter+' '+ipadd+' for '+a+': ')
    local('echo \"'+recnameA+'\t\tIN  A   '+ipforA+'\" >> '+os.getcwd()+'/recfold/'+ent+'.zone')
    serialReplacer()
    put(os.getcwd()+'/recfold/'+ent+'1.zone', bindpath+'/master/'+ent+'.zone')
    run('service named restart')

def addNSrec(bindpath):
    get(bindpath+'/master/'+ent+'.zone', os.getcwd()+'/recfold/')
    recnameNS = raw_input(''+enter+' '+ns+' name(For example: ns1.example.com. ): ')
    local('echo \"@\t\tIN  NS  '+recnameNS+'.\" >> '+os.getcwd()+'/recfold/'+ent+'.zone')
    serialReplacer()
    put(os.getcwd()+'/recfold/'+ent+'1.zone', bindpath+'/master/'+ent+'.zone')
    run('service named restart')
    print('You added '+ns+' but, each '+ns+' needs one '+a+'. Please add '+a+' for this NS.')
    addArec(bindpath)

def addMXrec(bindpath):
    get(bindpath+'/master/'+ent+'.zone', os.getcwd()+'/recfold/')
    recnameMX = raw_input(''+enter+' '+mx+' name(For example: newmail.example.com. ): ')
    MXprio = raw_input(''+enter+' '+mx+' priority number: ')
    local('echo \"@\t\tIN  MX  '+MXprio+'   '+recnameMX+'\" >> '+os.getcwd()+'/recfold/'+ent+'.zone')
    serialReplacer()
    put(os.getcwd()+'/recfold/'+ent+'1.zone', bindpath+'/master/'+ent+'.zone')
    run('service named restart')
    print('You added '+mx+' but, each '+mx+' needs one '+a+'. Please add '+a+' for this MX.')
    addArec(bindpath)

def addTXTrec(bindpath):
    get(bindpath+'/master/'+ent+'.zone', os.getcwd()+'/recfold/')
    #recnameTXT = raw_input(''+enter+' TXT record name(For example example.com. ): ')
    PTRip = raw_input(''+enter+' PTR '+ipadd+' for this '+txt+': ')
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
    print('You must add '+a+' for this '+recnameSRV+' FQDN.')
    addArec(bindpath)
    run('service named restart')

def recPrint(ent):
    print(''+ent+' domain name already exists...')
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
    recnameSRV = raw_input(''+enter+' FQDN for '+srv+' name(For example: jabber.example.com): ')
    global srvname 
    srvname = raw_input(''+enter+' service name for this '+srv+'(For example: _http, _ftp, _ldap): ')
    global prtcol
    prtcol = raw_input(''+enter+' protocol for this '+srv+'(For example: _tcp, _udp): ')
    global bdname
    bdname = raw_input(''+enter+' base domain name for this '+srv+'(For example: example.com): ')
    global prori
    prori = raw_input(''+enter+' priority for this '+srv+'(For example: 0-65535, Lowest is highest priority): ')
    global weight
    weight = raw_input(''+enter+' wight for this '+srv+'(For example: 0-65535, highest is most frequently delivered): ')
    global portnum
    portnum = raw_input(''+enter+' port number for this '+srv+'(For example: 80 for _http service): ')

env.user = raw_input(''+enter+' '+username+' for UNIX/Linux '+nserver+': ')
env.password = getpass.getpass(''+enter+' password for UNIX/Linux '+nserver+': ')

print('1. Write domain name which you want to update and press '+enter+' button: ')
print('2. To exit, press '+enter+' button. ')
ent = raw_input('Please input: ')

lzonename = 'cat /etc/named.conf | grep '+ent+' |  head -1 | awk \'{ print $2 }\' | sed \'s/"//g\''
lzonefile = 'cat /etc/named.conf | grep '+ent+' |  tail -1 | awk \'{ print $2 }\' | sed \'s/"//g;s/;//g\' | cut -f 5 -d\'/\' | cut -f1,2 -d \'.\''
fzonename = 'cat /usr/local/etc/namedb/named.conf | grep '+ent+' |  head -1 | awk \'{ print $2 }\' | sed \'s/"//g\''
fzonefile = 'cat /usr/local/etc/namedb/named.conf | grep '+ent+' |  tail -1 | awk \'{ print $2 }\' | sed \'s/"//g;s/;//g\' | cut -f 7 -d\'/\' | cut -f1,2 -d \'.\''

def writemzone(zname, zfile, bindpath, ent):
    if server == env.roledefs['dns'][0]:
        zonename = run(zname)
	zonefile = run(zfile)

        if ent == zonename and zonefile == ent:
            recPrint(ent)
            rec = raw_input('Write record type and press the enter button: ')

            if rec == "A":
                addArec(bindpath)
            elif rec == "NS":
                addNSrec(bindpath)
            elif rec == "MX":
                addMXrec(bindpath)
            elif rec == "TXT":
                addTXTrec(bindpath)
            elif rec == "SRV":
                addSRVrec(bindpath)
            else:
                print("This script only supports A, NS, MX, TXT and SRV record types.")

def checkPidDom(zname, zfile, bindpath, getbindpath, bindbin, pidfile, bindpid, ent):
    if getbindpath == bindbin and pidfile == bindpid:
        if ent != '' and len(ent) > 4:
            writemzone(zname, zfile, bindpath, ent)
            writeszone()
        else:
            print("\nMinimal symbol count must be 4.")
            sys.exit()

def checkDomainExists(zname, zfile, bindpath, getbindpath, bindbin, pidfile, bindpid, ent):
    if run(zname) == ent:
        checkPidDom(zname, zfile, bindpath, getbindpath, bindbin, pidfile, bindpid, ent)
    else:
        print(''+ent+' domain name does not exists in the remote '+nserver+'!!!')
        print('To add new domain use ./python-add-zone.py script.')
        sys.exit()

for server in env.roledefs['dns']:
    env.host_string = server
    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        osver = run('uname -s')
        lintype = run('cat /etc/redhat-release | awk \'{ print $1 }\'')
        ftype = run('uname -v | awk \'{ print $2 }\' | cut -f1 -d \'.\'')
        getbindpath = run('which named')
        bindpid = run('ps waux|grep named | grep -v grep | awk \'{ print $2 }\'')

        if osver == 'FreeBSD' and ftype >= 10:
            bindfpidfile = run('cat /var/run/named/pid')
            checkDomainExists(fzonename, fzonefile, fbindpath, getbindpath, bsdbindbin, bindfpidfile, bindpid, ent)

        elif osver == 'Linux' and lintype == 'CentOS':
            bindlpidfile = run('cat /var/run/named/named.pid')
            checkDomainExists(lzonename, lzonefile, cbindpath, getbindpath, cosbindbin, bindlpidfile, bindpid, ent)

        else:
            print("The script is not determine server type. For this reason you cannot use this script.")
