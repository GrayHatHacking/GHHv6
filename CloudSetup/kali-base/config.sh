#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get -y upgrade
apt-get -y dist-upgrade
echo "# Installing software properties common"
apt-get install -y software-properties-common gnupg
echo "# Attempting to install kali keys"
wget -q -O - https://archive.kali.org/archive-key.asc | apt-key add -
gpg --keyserver pgpkeys.mit.edu --recv-key  ED444FF07D8D0BF6
gpg -a --export ED444FF07D8D0BF6 | apt-key add -
echo deb http://http.kali.org/kali kali-rolling main non-free contrib > /etc/apt/sources.list.d/kali.list
apt-get update
apt-get install -y kali-linux-core kali-linux-default kali-linux-headless
