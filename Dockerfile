FROM ubuntu:latest
WORKDIR /home/
RUN git clone https://github.com/Klavishnik/AIAntiPlagiatForDock
WORKDIR AIAntiPlagiatForDock
RUN ./install.sh