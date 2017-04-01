#!/usr/bin/env python2.7
import sys
sys.path.insert(0, './lib')
from mslsvars import *
import os
from fabric.api import *
from fabric.tasks import execute
import getpass

env.roledefs = {
    'dns': [str(raw_input('Please '+enter+' NS1 '+ipadd+': ')), str(raw_input('Please '+enter+' NS2 '+ipadd+': '))]
}

env.user = raw_input('Please '+enter+' '+username+' for UNIX/Linux '+nserver+': ')
env.password = getpass.getpass('Please '+enter+' '+password+' for UNIX/Linux '+nserver+': ')

def commandER(osver, dnsuser):
    if osver == 'Linux':
        run('mkdir -p /var/log/bind/ /etc/namedb/{master,slave}')
        run('chown -R '+dnsuser+':'+dnsuser+' /var/log/bind/ /etc/namedb/{master,slave}')
        run('systemctl restart named')
    elif osver == 'FreeBSD':
        run('mkdir /var/log/bind/ ; chown -R '+dnsuser+':'+dnsuser+' /var/log/bind/')
        run('/usr/local/etc/rc.d/named restart')
    run('touch /var/log/bind/named.log /var/log/bind/query.log')

def bindWorker(pidfilepath, bindbin, osver):
    tempmVars = { "ns1" : env.roledefs['dns'][0], "ns2" : env.roledefs['dns'][1] }
    outputmText = tempm.render( tempmVars )
    outputsText = temps.render( tempmVars )
    outputlmText = templm.render( tempmVars )
    outputlsText = templs.render( tempmVars )
    bindpidfile = run(pidfilepath)

    if getbindpath == bindbin and bindpid == bindpidfile:
        print(' You have already installed and running bind in the '+server+' '+nserver+'...')
	print(' If you want add new domain, please use ./python-add-zone.py script. ')
        sys.exit()

    elif getbindpath != bindbin:
        print('Please be patient, script install and configure DNS Bind to the '+server+' '+nserver+'!!!')

    if osver == 'FreeBSD':
        run('pkg install -y bind910')
        run('echo named_enable="YES" >> /etc/rc.conf ; /usr/local/etc/rc.d/named start')

    elif osver == 'Linux':
	run('yum -y install bind bind-utils bind-chroot')
	run('systemctl enable named ; systemctl start named')

    if osver == 'FreeBSD' and server == env.roledefs['dns'][0]:
        print('Master DNS is '+successfully+' installed and configured on '+server+' '+nserver+'')
        with open(outputdir+'named_'+env.roledefs['dns'][0]+'.conf', 'wb') as ns1file:
            ns1file.write(outputmText)
        put(outputdir+'named_'+env.roledefs['dns'][0]+'.conf', '/usr/local/etc/namedb/named.conf')

    elif osver == 'FreeBSD' and server == env.roledefs['dns'][1]:
        print('Slave DNS is '+successfully+' installed and configured on '+server+' '+nserver+'')
        with open(outputdir+'named_'+env.roledefs['dns'][1]+'.conf', 'wb') as ns2file:
            ns2file.write(outputsText)
        put(outputdir+'named_'+env.roledefs['dns'][1]+'.conf', '/usr/local/etc/namedb/named.conf')

    if osver == 'Linux' and server == env.roledefs['dns'][0]:
        print('Master DNS is '+successfully+' installed and configured on '+server+' '+nserver+'')
        with open(outputdir+'lnamed_'+env.roledefs['dns'][0]+'.conf', 'wb') as ns1file:
            ns1file.write(outputlmText)
        put(outputdir+'lnamed_'+env.roledefs['dns'][0]+'.conf', '/etc/named.conf')

    elif osver == 'Linux' and server == env.roledefs['dns'][1]:
        print('Slave DNS is '+successfully+' installed and configured on '+server+' '+nserver+'')
        with open(outputdir+'lnamed_'+env.roledefs['dns'][1]+'.conf', 'wb') as ns2file:
            ns2file.write(outputlsText)
        put(outputdir+'lnamed_'+env.roledefs['dns'][1]+'.conf', '/etc/named.conf')

for server in env.roledefs['dns']:
    env.host_string = server

    with settings( hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        osver = run('uname -s')
        lintype = run('cat /etc/redhat-release | awk \'{ print $1 }\'')
        ftype = run('uname -v | awk \'{ print $2 }\' | cut -f1 -d \'.\'')
        getbindpath = run('which named')
        bindpid = run('ps waux | grep named | grep -v grep | awk \'{ print $2 }\'')

        if osver == 'FreeBSD' and ftype >= 10:
            bindWorker(bsdbindpidfile, bsdbindbin, osver)
            commandER(osver, 'bind')
            print('It was '+freebsd+' '+nserver+'')

        elif osver == 'Linux' and lintype == 'CentOS':
            bindWorker(cosbindpidfile, cosbindbin, osver)
            commandER(osver, 'named')
            print('It was '+centos+' server')

        else:
            print('The script is not determine '+server+' type. For this reason you cannot use this script.')
