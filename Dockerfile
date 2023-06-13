FROM ubuntu:latest
WORKDIR /home/
RUN apt update && apt-get install -y git
RUN git clone https://github.com/Klavishnik/AIAntiPlagiatForDock
WORKDIR AIAntiPlagiatForDock
RUN ./install.sh