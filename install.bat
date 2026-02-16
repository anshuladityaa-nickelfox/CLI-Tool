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
echo    mkdir %USERPROFILE%\.nfxinit
echo    copy .env.example %USERPROFILE%\.nfxinit\.env
echo    notepad %USERPROFILE%\.nfxinit\.env
echo.
echo 2. Run from anywhere:
echo    NFXinit
echo.
echo ========================================
pause
