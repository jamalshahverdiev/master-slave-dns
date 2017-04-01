import os
import jinja2
from termcolor import colored, cprint

codepath = os.getcwd()
jinjadir = codepath+'/j2temps/'
outputdir = codepath+'/outdir/'

templateLoader = jinja2.FileSystemLoader( searchpath=jinjadir )
templateEnv = jinja2.Environment( loader=templateLoader )
TEMPMFILE = 'fmnamed.conf.j2'
TEMPSFILE = 'fsnamed.conf.j2'
TEMPLMFILE = 'lmnamed.conf.j2'
TEMPLSFILE = 'lsnamed.conf.j2'

#### Input colors
ipadd = colored('IP address', 'green', attrs=['bold', 'underline'])
username = colored('username', 'green', attrs=['bold', 'underline'])
password = colored('password', 'magenta', attrs=['bold', 'underline'])
successfully = colored('successfully', 'green', attrs=['bold', 'underline'])
centos = colored('CentOS', 'yellow', attrs=['bold', 'underline'])
freebsd = colored('FreeBSD', 'yellow', attrs=['bold', 'underline'])
enter = colored('Enter', 'cyan', attrs=['bold', 'underline'])
nserver = colored('server', 'cyan', attrs=['bold', 'underline'])

#### Record colors
mx = colored('MX record', 'green', attrs=['bold', 'underline'])
a = colored('A record', 'green', attrs=['bold', 'underline'])
ns = colored('NS record', 'magenta', attrs=['bold', 'underline'])
txt = colored('TXT record', 'yellow', attrs=['bold', 'underline'])
srv = colored('SRV record', 'cyan', attrs=['bold', 'underline'])

tempm = templateEnv.get_template( TEMPMFILE )
temps = templateEnv.get_template( TEMPSFILE )
templm = templateEnv.get_template( TEMPLMFILE )
templs = templateEnv.get_template( TEMPLSFILE )

cbindpath = '/etc/namedb'
fbindpath = '/usr/local/etc/namedb'
bsdbindbin = '/usr/local/sbin/named'
bsdbindpidfile = 'cat /var/run/named/pid'
cosbindbin = '/usr/sbin/named'
cosbindpidfile = 'cat /var/run/named/named.pid'
