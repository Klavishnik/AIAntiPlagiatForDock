#!/bin/bash

# Check if virtualenv is installed
if ! command -v virtualenv &> /dev/null
then
    echo "virtualenv not found, installing..."
    pip install virtualenv
fi

# Create and activate virtual environment
virtualenv venv
source venv/bin/activate

# Install dependencies
sudo apt install python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils pstotext tesseract-ocr flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig
pip install -r requirements.txt

echo "Installation complete. To activate the virtual environment, run 'source venv/bin/activate'"