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


mkdir tmp roberta-base-openai-detector roberta-large-openai-detector

git clone https://huggingface.co/roberta-large-openai-detector
git clone https://huggingface.co/roberta-base-openai-detector


cp tmp/roberta-base-openai-detector/config.json /roberta-base-openai-detector
cp tmp/roberta-base-openai-detector/merges.txt /roberta-base-openai-detector
cp tmp/roberta-base-openai-detector/pytorch_model.bin /roberta-base-openai-detector
cp tmp/roberta-base-openai-detector/tokenizer.json /roberta-base-openai-detector
cp tmp/roberta-base-openai-detector/vocab.json /roberta-base-openai-detector


cp tmp/roberta-large-openai-detector/config.json /roberta-large-openai-detector
cp tmp/roberta-large-openai-detector/merges.txt /roberta-large-openai-detector
cp tmp/roberta-large-openai-detector/pytorch_model.bin /roberta-large-openai-detector
cp tmp/roberta-large-openai-detector/tokenizer.json /roberta-large-openai-detector
cp tmp/roberta-large-openai-detector/vocab.json /roberta-large-openai-detector

rm -rf tmp

#source venv/bin/activate