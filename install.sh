#!/bin/bash
# run with sudo
# Check if virtualenv is installed
apt update
apt install -y python3 python3-dev pip libxml2-dev libxslt1-dev antiword unrtf poppler-utils pstotext tesseract-ocr flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig libpulse-dev
               

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


git clone https://huggingface.co/roberta-large-openai-detector
cd roberta-large-openai-detector/ 
rm -rf flax_model.msgpack .git*  README.md vocab.json

git clone https://huggingface.co/roberta-base-openai-detector
cd roberta-base-openai-detector/ 
rm -rf flax_model.msgpack .git*  README.md vocab.json

#source venv/bin/activate