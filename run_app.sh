#!/bin/bash

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Navigate into route_data directory
echo "Navigating to route_data folder..."
cd route_data

# Run database_builder.py
echo "Running database_builder.py..."
python database_builder.py

# Navigate back to the original directory
echo "Navigating back to the original directory..."
cd ..

# Run data.py in the background
echo "Running data.py in the background..."
python data.py &

# Run app.py
echo "Running app.py..."
python app.py
