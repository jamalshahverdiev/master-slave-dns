<html>
<meta charset="utf-8">
The content of this branch are the following:
<center><b>dnscleaner.sh
python-installer.sh
jinja2temps
python-ms-sl-dns.py
python-add-zone.py</b></center>

<b>dnscleaner.sh</b>  - is SHELL script which cleans everything about DNS BIND.

<b>python-installer.sh</b> - This script will check the operating system and install python2.7 and python3.4

<b>jinja2temps</b> - This folder contains templates for DNS Bind configuration.

<b>python-ms-sl-dns.py</b> - If you execute this script first time, this will get IP for Master and Slave DNS servers.
                        After that it will install DNS Bind to them.
                        If you  execute this script second time, it will check DNS service on Master and Slave DNS server.
                        If service  works, it will prompt please use ./python-add-zone.py script for add new zone.

<b>python-add-zone.py</b> - For adding new Zone execute this script and write domain name. This will create named.conf configurations for master and Slave servers and will create domain file.

By default Fabric is searching for <b>/bin/bash</b> binary file(Install bash with <b>python-installer.sh</b> script). That is why I have copied <b>/usr/local/bin/bash</b> file to <b>/bin/bash</b> in FreeBSD Servers. Also copy of content of <b>freebsd-bash</b> folder to the <b>/root</b> homefolder for FreeBSD servers.
</html>
