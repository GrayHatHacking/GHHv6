#!/bin/bash

cd kali-base
packer build kali.json
cd ../server-2016-base
packer build server2016_template.json
cd ../server-2019-base
packer build server2019_template.json
cd ..
