@echo off

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Navigate to the route_data subdirectory
echo Navigating to route_data folder...
cd route_data

REM Run database_builder.py
echo Running database_builder.py...
python database_builder.py

REM Navigate back to the original directory
echo Navigating back to the original directory...
cd ..

REM Run data.py in the background
echo Running data.py in the background...
start /b python data.py

REM Run app.py
echo Running app.py...
python app.py
