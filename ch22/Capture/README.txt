The capture files are included with the names reflected the device, command, sample rate, and tuned frequency.

Ubuntu Version used in the lab:
        Distributor ID: Ubuntu
        Description:    Ubuntu 20.04.2 LTS
        Release:        20.04
        Codename:       focal

hackrf firmware version:
	hackrf_info version: git-704725217d
	libhackrf version: git-704725217d (0.6)
	Found HackRF
	Index: 0
	Serial number: 0000000000000000457863c82f57531f
	Board ID Number: 2 (HackRF One)
	Firmware Version: 2021.03.1 (API:1.04)
	Part ID Number: 0xa000cb3c 0x005c4737

Installing Pybombs,GNU Radio, and Hackrf Tools:
        You will need to install GNU Radio, hackrf tools, and osmosdr tools.  The following commands will install these tools using pybombs.  While not likely an issue, pybombs will install from the head of the repositories; therefore, the actual versions will differ from what is used in the book.  For these exercises, Python 3 is recommended.

        mkdir ~/Documents/sdr
        cd ~/Documents/sdr
        sudo apt-get install git
        sudo apt-get install python3-pip
        sudo pip3 install --upgrade pip
        sudo pip3 install --upgrade git+https://github.com/gnuradio/pybombs.git
        sudo pybombs auto-config
        sudo pybombs recipes add-defaults
        sudo pybombs prefix init ~/Documents/sdr/prefix2 -a myprefix -R gnuradio-default
        sudo pybombs install hackrf
        sudo pybombs install gr-osmosdr


Versions installed by pybombs for the exercises:
	airspy        022870fd88c026c124683fa58531a3a70181ebe9
	airspyhf      2bf53e127a0122e18f72d4cc89b5c512d286d953
	bladeRF       06a29713be6b4a9d6043be36c83d8778ff8b19c9
	gnuradio      9d94c8a675d085082304bf96e5b30a46bbb8bb9e
	gr-fcdproplus 575fcafbb8f36dc11d95a305f331660612a44596
	gr-iqbal      f56d917c83074ed93e9b47071b8f3a695796f0d8
	gr-osmosdr    cffef690f29e0793cd2d6c5d028c0c929115f0ac
	hackrf        704725217ded60889f4a3887084f8d16e04b1a94
	libosmo-dsp   551b9752bcd5d3d21bb2df0736b1801bda3d0d10
	libvolk       237a6fc9242ea8c48d2bbd417a6ea14feaf7314a
	osmo-sdr      ba4fd96622606620ff86141b4d0aa564712a735a
	rtl-sdr       0847e93e0869feab50fd27c7afeb85d78ca04631
	soapysdr      1cf5a539a21414ff509ff7d0eedfc5fa8edb90c6
	uhd           1b60cf86d39354b5e46f4e250b9e59758ac50ec9

Included Files:
	remote_analysis.grc - The flow graph for the capture

Captured Signals:
	remote1-1on-4m-316mhz   
	remote1-1off-4m-316mhz  
	remote1-2on-4m-316mhz   
	remote1-2off-4m-316mhz  
	remote1-3off-4m-316mhz  
	remote1-3on-4m-316mhz   
	remote2-1on-4m-316mhz   
	remote2-2on-4m-316mhz   
	remote2-3on-4m-316mhz
	remote2-1off-4m-316mhz  
	remote2-2off-4m-316mhz  
	remote2-3off-4m-316mhz

