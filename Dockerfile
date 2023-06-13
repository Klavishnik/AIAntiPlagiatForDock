FROM ubuntu:lastest
WORKDIR /home/
RUN apt update && apt-get install -y git vim
RUN git clone https://github.com/Klavishnik/AIAntiPlagiatForDock && cd AIAntiPlagiatForDock
RUN ./install.sh