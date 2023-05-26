#Create directory
sudo mkdir user
cd user

#Preliminary installs
sudo apt-get update
sudo apt-get -y install python3.8
sudo apt-get -y install git 

#Download and set up docker
sudo apt-get install -y docker.io
groupadd docker 
sudo gpasswd -a alredoone docker
sudo newgrp docker
sudo service docker restart

#Download docker-compose
sudo curl -L https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

#Clone repository
sudo git clone https://github.com/ajohnson5/fpl-classic-pipeline.git
cd fpl-classic-pipeline
sudo git switch main

#Create and populate .env file
sudo touch .env
sudo echo "PROJECT_ID=${PROJECT_ID}" >> .env
sudo echo "PROJECT_DATASET=${PROJECT_DATASET}" >> .env
sudo echo "PROJECT_BUCKET=${PROJECT_BUCKET}" >> .env
sudo echo "LEAGUE_ID=${LEAGUE_ID}" >> .env
sudo echo "POSTGRES_USERNAME=${POSTGRES_USERNAME}" >> .env
sudo echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" >> .env
sudo echo "POSTGRES_DB=${POSTGRES_DB}" >> .env

#Run docker-compose
docker-compose build
docker-compose up -d

