#!/usr/bin/env bash

ssh-keygen -t rsa -b 4096 -f ./keys -q -N ""

publicKey=$(<keys.pub)

az bicep build --file main.bicep

az deployment sub create \
    --location germanywestcentral \
    --name azure-vm-exp \
    --template-file main.json \
    --parameters publicKey="$publicKey"
