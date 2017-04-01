#!/usr/bin/env python2.7
import getpass
import os
import sys
sys.path.insert(0, './lib')
from zonevars import *
from fabric.api import *
from fabric.tasks import execute

env.roledefs = {
    'dns': [str(raw_input('Please enter NS1 '+ipadd+': ')), str(raw_input('Please enter NS2 '+ipadd+': '))]
}

env.user = raw_input('Please enter username for UNIX/Linux '+nserver+': ')
env.password = getpass.getpass('Please enter '+password+' for UNIX/Linux '+nserver+': ')

print('1. Write domain name and press '+enter+' button.')
print('2. To exit, press '+enter+' button. ')
ent = raw_input('Please input: ')

def domainchecker(conf):
    if server == env.roledefs['dns'][0]:
        fzonename = run('cat '+conf+' | grep '+ent+' |  head -1 | awk \'{ print $2 }\' | sed \'s/"//g\'')
        fzonefile = run('cat '+conf+' | grep '+ent+' |  tail -1 | awk \'{ print $2 }\' | sed \'s/"//g;s/;//g\' | awk -F/ \'{print $NF}\' | cut -f1,2 -d\'.\'')
        if ent == fzonename and fzonefile == ent:
            print(' Entered domain name '+ent+' already exists in the NS1 '+env.roledefs['dns'][0]+' '+nserver+'!!!')
            print(' If you want add new record for this '+ent+' domain name, please use ./python-add-record.py script.')
            sys.exit()
        else:
            pass

def writemzone(bindpath, conf):
    tempmzVars = { "ns1" : env.roledefs['dns'][0], "ns2" : env.roledefs['dns'][1], "domain" : ent, "bdpath" : bindpath }
    outputmzText = tempmz.render( tempmzVars )
    outputdomText = tempdom.render( tempmzVars )
    if server == env.roledefs['dns'][0]:
        with open(outputdir+'zone_'+env.roledefs['dns'][0]+'.conf', 'wb') as ns1zone:
            ns1zone.write(outputmzText)
        with open(outputdir+ent+'.zone', 'wb') as masdom:
            masdom.write(outputdomText)
        print(''+successfully+' configured for '+env.roledefs['dns'][0]+' '+nserver+'')
        put(outputdir+'zone_'+env.roledefs['dns'][0]+'.conf', ''+bindpath+'')
        put(outputdir+ent+'.zone', ''+bindpath+'/master/')
        run('cat '+bindpath+'/zone_'+env.roledefs['dns'][0]+'.conf >> '+conf+'')
        run('service named restart')

def writeszone(bindpath, conf):
    tempszVars = { "ns1" : env.roledefs['dns'][0], "domain" : ent, "bdpath" : bindpath}
    outputszText = tempsz.render( tempszVars )
    if server == env.roledefs['dns'][1]:
        with open(outputdir+'zone_'+env.roledefs['dns'][1]+'.conf', 'wb') as ns2zone:
            ns2zone.write(outputszText)
        print(''+successfully+' configured for '+env.roledefs['dns'][1]+' '+nserver+'')
        put(outputdir+'zone_'+env.roledefs['dns'][1]+'.conf', ''+bindpath+'')
        run('cat '+bindpath+'/zone_'+env.roledefs['dns'][1]+'.conf >> '+conf+'')
        run('service named restart')

def checkservice():
    print(' DNS service does not working!!!')
    print(' To install DNS bind please use, ./python-ms-sl-dns.py script. ')
    sys.exit()

def checkBIND(pidpath, bindpid, bindbin, conffile, bindpath):
    bindpidfile = run(pidpath)
    if getbindpath == bindbin and bindpid == bindpidfile:
        domainchecker(conffile)

        if ent != '' and len(ent) > 4:
            writemzone(bindpath, conffile)
            writeszone(bindpath, conffile)
        else:
            print("\nMinimal symbol count can be 4.")
            sys.exit()
    else:
        checkservice()

for server in env.roledefs['dns']:
    env.host_string = server
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'),
        warn_only=True
    ):
        osver = run('uname -s')
        lintype = run('cat /etc/redhat-release | awk \'{ print $1 }\'')
        ftype = run('uname -v | awk \'{ print $2 }\' | cut -f1 -d \'.\'')
        getbindpath = run('which named')
        bindpid = run('ps waux | grep named | grep -v grep | awk \'{ print $2 }\'')

        if osver == 'FreeBSD' and ftype >= 10:
            checkBIND(fpidpath, bindpid, bsdbindbin, fbconf, fbindpath)
        elif osver == 'Linux' and lintype == 'CentOS':
            checkBIND(lpidpath, bindpid, cosbindbin, cbconf, cbindpath)
        else:
            print("The script is not determine server type. For this reason you cannot use this script.")
