#!/bin/sh

set -o errexit
set -o nounset

IFS=$'\n\r'

# Docker
sudo apt update
sudo apt --yes --no-install-recommends install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update
sudo apt --yes --no-install-recommends install docker-ce
sudo usermod --append --groups docker "$USER"
sudo systemctl enable docker
printf '\nDocker installed successfully\n\n'

