echo "Installs pre-requisites for lab"

sudo apt-get install qtbase5-dev libfftw3-dev cmake pkg-config libliquid-dev
git clone https://github.com/miek/inspectrum.git
cd inspectrum/
mkdir build
cd build/
cmake ..
make
sudo make install

sudo apt-get install ipython3
pip3 install bitstring
