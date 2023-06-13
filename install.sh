#!/bin/bash
# run with sudo
# Check if virtualenv is installed
apt update
apt install -y python3 python3-dev pip libxml2-dev libxslt1-dev antiword unrtf poppler-utils pstotext tesseract-ocr flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig libpulse-dev vim curl
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash
apt-get install git-lfs
        

if ! command -v virtualenv &> /dev/null
then
    echo "virtualenv not found, installing..."
    pip install virtualenv
fi

# Create and activate virtual environment
virtualenv venv
source venv/bin/activate

# Install dependencies

pip install -r requirements.txt

echo "Installation complete. To activate the virtual environment, run 'source venv/bin/activate'"

git lfs install
git clone  https://huggingface.co/roberta-large-openai-detector roberta-large-openai-detector
git clone  https://huggingface.co/roberta-base-openai-detector roberta-base-openai-detector

#source venv/bin/activate