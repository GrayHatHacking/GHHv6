# The lab was performed on Kali 2021.1
# The following commands will install binwalk for the exercise.

sudo apt-get update

# REMOVE the older binwalk
sudo apt-get --purge remove binwalk

sudo apt install python3-pip

git clone https://github.com/ReFirmLabs/binwalk.git
cd binwalk
# checkout a known working version of binwalk
git checkout 772f271

# Need to apply a patch to build sasquatch and correct an issue with installing QT
sed -i "s#qt5base-dev#qtbase5-dev#; s#cd sasquatch \&\& \$SUDO \./build\.sh#cd sasquatch \&\& CFLAGS=-fcommon \$SUDO \./build\.sh#" deps.sh

./deps.sh

sudo python3 setup.py install
