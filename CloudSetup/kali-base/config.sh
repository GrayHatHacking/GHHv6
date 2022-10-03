#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
ERRORS=0
apt-get update && apt-get -y upgrade
apt-get -y dist-upgrade


echo "# Installing software properties common"
apt-get install -y software-properties-common gnupg
echo "# Attempting to install kali keys"
wget -q -O - https://archive.kali.org/archive-key.asc | apt-key add -
gpg --keyserver pgpkeys.mit.edu --recv-key  ED444FF07D8D0BF6
gpg -a --export ED444FF07D8D0BF6 | apt-key add -
echo deb http://http.kali.org/kali kali-rolling main non-free contrib > /etc/apt/sources.list.d/kali.list
echo 'Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries

apt-get update

echo "#Trying to install Kali components"
apt-get install -y kali-linux-headless || ERRORS=1 

if [ $ERRORS -ne 0 ] ;then
  echo "# Fixing Lincryopt... "
  pushd .
  cd /tmp
  apt -y download libcrypt1 
  dpkg-deb -x libcrypt*  .
  cp -av lib/x86_64-linux-gnu/* /lib/x86_64-linux-gnu/
  popd 
fi

apt -y --fix-broken install
service sshd restart

echo "# Provisioning complete"
exit 0
