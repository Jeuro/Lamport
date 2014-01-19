#!/bin/bash

while read id host port; do
    termite -e "bash -c 'python client.py config $id; bash'" &
done < config