import os
import jinja2
from termcolor import colored, cprint

ipadd = colored('IP address', 'green', attrs=['bold', 'underline'])
successfully = colored('Successfully', 'green', attrs=['bold', 'underline'])
username = colored('username', 'green', attrs=['bold', 'underline'])
password = colored('password', 'magenta', attrs=['bold', 'underline'])
enter = colored('Enter', 'cyan', attrs=['bold', 'underline'])
nserver = colored('server', 'cyan', attrs=['bold', 'underline'])

codepath = os.getcwd()
jinjadir = codepath+'/j2temps/'
outputdir = codepath+'/outdir/'

templateLoader = jinja2.FileSystemLoader( searchpath=jinjadir )
templateEnv = jinja2.Environment( loader=templateLoader )
TEMPMZFILE = 'fmnewzone.conf.j2'
TEMPSZFILE = 'fsnewzone.conf.j2'
TEMPDOMFILE = 'mszone.conf.j2'

tempmz = templateEnv.get_template( TEMPMZFILE )
tempsz = templateEnv.get_template( TEMPSZFILE )
tempdom = templateEnv.get_template( TEMPDOMFILE )

cbconf = '/etc/named.conf'
cbindpath = '/etc/namedb'
cosbindbin = '/usr/sbin/named'
bsdbindbin = '/usr/local/sbin/named'
fbconf = '/usr/local/etc/namedb/named.conf'
fbindpath = '/usr/local/etc/namedb'

fpidpath = 'cat /var/run/named/pid'
lpidpath = 'cat /var/run/named/named.pid'
