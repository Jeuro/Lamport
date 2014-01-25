#!/bin/bash

config_file="$1"
mkdir -p out

while read id host port; do
    ssh -t -t -o "StrictHostKeyChecking no" $host "cd $(pwd); python3 client.py $config_file $id" 2> /dev/null &
done < $config_file
wait
