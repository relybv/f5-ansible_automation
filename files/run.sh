#!/bin/bash
# run this script from cron to provision planned changes
F5_PLANNED=true

# check env variables, do not use parameters to scripts as they show in the proccess list and is a security risk
if [ -z "$F5_DBUSER" ]; then
    echo "Need to set F5_DBUSER"
    exit 1
fi  
if [ -z "$F5_DBPASSWD" ]; then
    echo "Need to set F5_DBPASSWD"
    exit 1
fi
if [ -z "$F5_LBUSER" ]; then
    echo "Need to set F5_LBUSER"
    exit 1
fi
if [ -z "$F5_LBPASSWD" ]; then
    echo "Need to set F5_LBPASSWD"
    exit 1
fi

# install network, addresses, vlans and certificate
ansible-playbook -i files/inventory.py tasks/network.yml
if [ "$?" -ne 0 ]; then
    echo "ansible-playbook exited with non-zero status"
fi

# install customer iapp
files/inventory.py | xvfb-run ruby files/f5-iapp.rb -v
if [ "$?" -ne 0 ]; then
    echo "f5-iapp.rb command exited with non-zero status"
fi
