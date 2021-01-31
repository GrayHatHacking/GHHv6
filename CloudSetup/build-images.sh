#!/bin/bash

cd kali-base
/usr/bin/packer build kali.json
cd ../server-2016-base
/usr/bin/packer build server2016_template.json
cd ../server-2019-base
/usr/bin/packer build server2019_template.json
cd ..
