#!/bin/bash
PACKER=/usr/bin/packer
if [  -f ~/.local/bin/packer ] ; then 
	PACKER=~/.local/bin/packer
fi
cd kali-base
$PACKER build kali.json
cd ../server-2016-base
$PACKER server2016_template.json
cd ../server-2019-base
$PACKER server2019_template.json
cd ..
