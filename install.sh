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
pip install -r requirements.txt

echo "Installation complete. To activate the virtual environment, run 'source venv/bin/activate'"