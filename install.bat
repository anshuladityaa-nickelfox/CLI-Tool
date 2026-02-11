@echo off
echo ========================================
echo Installing Django Project Generator
echo ========================================
echo.

echo Installing package globally...
pip install -e .

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Set up your API key:
echo    mkdir %USERPROFILE%\.initiatep
echo    copy .env.example %USERPROFILE%\.initiatep\.env
echo    notepad %USERPROFILE%\.initiatep\.env
echo.
echo 2. Run from anywhere:
echo    initiatep
echo.
echo ========================================
pause
