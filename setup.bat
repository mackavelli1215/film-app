@echo off
REM FilmApp Setup Script for Windows
REM Run this script to set up the complete development environment

echo.
echo =====================================================
echo FilmApp - Film Production Management Platform Setup
echo =====================================================
echo.

echo [1/7] Creating Python virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment. Make sure Python 3.11+ is installed.
    pause
    exit /b 1
)

echo [2/7] Activating virtual environment...
call .venv\Scripts\activate

echo [3/7] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies.
    pause
    exit /b 1
)

echo [4/7] Installing Node.js dependencies...
npm install
if errorlevel 1 (
    echo ERROR: Failed to install Node.js dependencies. Make sure Node.js 20+ is installed.
    pause
    exit /b 1
)

echo [5/7] Building Tailwind CSS...
npm run build:css
if errorlevel 1 (
    echo WARNING: Failed to build CSS. You can run 'npm run build:css' manually later.
)

echo [6/7] Setting up database...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to run database migrations.
    pause
    exit /b 1
)

echo [7/7] Creating initial sample data...
python init_data.py

echo.
echo =====================================================
echo Setup completed successfully!
echo =====================================================
echo.
echo Next steps:
echo 1. Update your .env file with real Supabase credentials
echo 2. Create a superuser: python manage.py createsuperuser  
echo 3. Start the server: python manage.py runserver
echo 4. In another terminal: python manage.py run_agents --once
echo.
echo Access your application at: http://localhost:8000
echo.
pause