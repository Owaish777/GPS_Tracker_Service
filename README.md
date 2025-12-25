# GPS_Tracker_Service

# Requirements: Python 3.9+
# Setup commands:

## Create a virtual environment( venv )
# Windows
py -3.9 -m venv venv
# macOS / Linux
python3.9 -m venv venv


## Activate the venv
# Windows (Command Prompt)
venv\Scripts\activate
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate


## Install the dependencies 
python -m pip install -r requirements.txt


## Test locally 
# Activate the venv 
venv\Scripts\activate

# Error: "Unable to match the identifier name ProcessSet-ExecutionPolicy to a valid enumerator name. Then
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Start the server
python app.py
