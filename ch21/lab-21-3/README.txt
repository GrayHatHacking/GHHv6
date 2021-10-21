Lab performed on kali-linux-2021.1-installer-amd64.iso

1. Install build essentials and git
sudo apt-get install build-essential git telnet

2.  Pulled and installed FirmAE
git clone --recursive https://github.com/pr0v3rbs/FirmAE
cd FirmAE
./download.sh
./install.sh
./init.sh

