
* The content of this branch are the following::
  
    dnscleaner.sh
    python-installer.sh
    jinja2temps
    python-ms-sl-dns.py
    python-add-zone.py

* Short explanation for scripts and folders:

========================   ======================================================================================================
Name                       Description
========================   ======================================================================================================
``dnscleaner.sh``          SHELL script which cleans everything about DNS BIND.
``python-installer.sh``    This script will check the operating system and install python2.7 and python3.4
``jinja2temps``            This folder contains templates for DNS Bind configuration.
``python-ms-sl-dns.py``    If you execute this script first time, this will get IP for Master and Slave DNS servers.
``python-add-zone.py``     For adding new Zone execute this script and write domain name. 
=======================    ======================================================================================================

* By default Fabric is searching for **/bin/bash** binary file(Install bash with **python-installer.sh** script). That is why I have copied ``/usr/local/bin/bash`` file to ``/bin/bash`` in FreeBSD Servers. Also copy the content of **freebsd-bash** folder to the **/root** homefolder for FreeBSD servers.
