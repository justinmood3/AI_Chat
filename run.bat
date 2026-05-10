@echo off
REM Justin AI - Startup Script

echo.
echo ================================
echo  Justin AI Chat Application
echo ================================
echo.

REM Check if database.db exists
if exist database.db (
    echo Database found.
) else (
    echo Creating new database...
)

REM Run the Flask app
echo Starting Flask server...
echo.
echo The app will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python.exe app.py

pause
