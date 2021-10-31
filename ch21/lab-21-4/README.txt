Note: Running sudo with -E as some pip installations are not available in the root user's environment.  Ubuntu 18.04 didn't appear to suffer from this problem, but 20.04 would not find binwalk if not run with the users environment.

Note2: The firmware was renamed to use underscore instead of spaces for convenience.
1. Copy the firmware into FirmAE directory

2. From the FirmAE directory, check the network.
sudo -E ./run.sh -c netgear WNAP320_Firmware_Version_2.0.3.zip

3. Emulate the firmware in debug mode.  This affords the user with more control over the process.
sudo -E ./run.sh -d netgear WNAP320_Firmware_Version_2.0.3.zip

4. At this point, you can use a browser and verify the system is operational.  The emulation will stop one you exit the menu (6).
