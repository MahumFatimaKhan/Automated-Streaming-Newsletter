@echo off
echo ========================================
echo Starting Newsletter Generator
echo ========================================
echo.

echo Checking ChromeDriver...
if not exist chromedriver-win64\chromedriver.exe (
    echo ChromeDriver not found!
    echo Please ensure chromedriver.exe is in the chromedriver-win64 folder
    pause
    exit
)

echo ChromeDriver found in chromedriver-win64 folder
echo Starting Flask application...
python app.py

pause