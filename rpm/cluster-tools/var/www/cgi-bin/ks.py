#!/usr/bin/python
import sys
import os
import socket
sys.stderr = sys.stdout
print "Content-Type: text/plain"
print

extra_pacakges = ""
installnode = "10.1.1.1"
clustername = "fgi"
installurl = ""
securityurl = ""
fgiurl = ""
epelurl = ""
localurl = ""
disk-config = ""


try:
 clusterconf = open("/etc/cluster/conf/cluster.conf")
 clustersettings = {}
 for line in clusterconf.readlines():
  #for every line, e.g. "key=value", set clusterconf["key"]="value"
  clustersettings[line.split("=")[0]] = line.split("=")[1].strip()
 
 installnode = clustersettings["INSTALLNODEIP"]
 clustername = clustersettings["CLUSTERNAME"]
 installurl = "url --url %s" % clustersettings["OS_REPOURL"]
 proxy = clustersettings["LOGINNODEIP"]
 securityurl = 'repo --name="Scientific Linux 6 - Security updates" --baseurl=%s --proxy=http://%s:8080/' % (clustersettings["OS_SECURITY_REPOURL"], proxy)
 fgiurl = 'repo --name="FGI" --baseurl=%s --proxy=http://%s:8080/' % (clustersettings["FGI_REPOURL"], proxy)
 epelurl = 'repo --name="epel" --baseurl=%s --proxy=http://%s:8080/' % (clustersettings["FGI_REPOURL"], proxy)
 if "LOCAL_REPOURL" in clustersettings and len(clustersettings["LOCAL_REPOURL"]) > 0 :
  localurl = 'repo --name="local" --baseurl=%s --proxy=http://%s:8080/' % (clustersettings["LOCAL_REPOURL"], proxy)
 hostname = socket.gethostbyaddr(os.environ["REMOTE_ADDR"])[0].split(".")[0]
 f = open("/etc/cluster/nodes/" + hostname + "/packages")
 extra_packages = f.read()
 f.close()
 try:
  f = open("/etc/cluster/nodes/" + hostname + "/disk-config")
  disk-config = f.read()
  f.close()
 except:
  disk-config = '''bootloader --location=mbr --driveorder=cciss/c0d0
clearpart --all --drives=cciss/c0d0
part /boot    --fstype ext3 --size 1000     --asprimary     --ondrive=cciss/c0d0
part /    --fstype ext4 --size 1 --grow                 --ondrive=cciss/c0d0'''
  
except:
  pass

print '''
install
%s
%s
%s
%s
reboot

lang en_US.UTF-8
keyboard fi
vnc

network --device eth4 --bootproto dhcp
firewall --disabled
selinux --disabled
rootpw --iscrypted $1$g2Ge6Ann$EZZrUtyBZ5tf6ESA95Tey1
authconfig --enablenis --nisserver %s --nisdomain %s
timezone --utc Europe/Helsinki

services --enabled ypbind,slurm,munge,nscd,ntpd,gmond

zerombr
%s

%post
modprobe nfs
mount -tnfs %s:/etc/cluster /mnt
for script in /mnt/scripts/* ; do
 "$script"
done
umount /mnt

%packages
@infiniband
openssh-server
ypbind
nfs-utils
munge
slurm-munge
slurm
nscd
pdsh
ganglia-gmond
openmpi
'''  % (installurl, securityurl, fgiurl, epelurl, localurl, installnode, clustername, disk-config, installnode)
print extra_packages
