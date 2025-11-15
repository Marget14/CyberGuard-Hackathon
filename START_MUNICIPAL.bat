@echo off
REM ==========================================
REM CyberGuard - Municipal Edition Launcher
REM Δήμος Αθηναίων
REM ==========================================

setlocal enabledelayedexpansion
color 0B
cls

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║                                                        ║
echo ║    🛡️  CYBERGUARD - MUNICIPAL EDITION                ║
echo ║    Δήμος Αθηναίων                                     ║
echo ║    Προστασία από Απατηλά Emails                       ║
echo ║                                                        ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ ΣΦΑΛΜΑ: Python δεν βρέθηκε!
    echo Εγκαταστήστε Python 3.13+ από: https://www.python.org
    echo.
    pause
    exit /b 1
)

python --version
echo.

REM Check files
echo 📋 Έλεγχος αρχείων...
if not exist "CyberGuard_API.py" (
    color 0C
    echo ❌ CyberGuard_API.py δεν βρέθηκε!
    pause
    exit /b 1
)

if not exist "CyberGuard_Municipal_Edition.py" (
    color 0C
    echo ❌ CyberGuard_Municipal_Edition.py δεν βρέθηκε!
    pause
    exit /b 1
)

echo ✅ Όλα τα αρχεία παρόντα
echo.

REM Start API Server
echo 🌐 Εκκίνηση API Server...
start "CyberGuard API Server" python CyberGuard_API.py

REM Wait
timeout /t 3 /nobreak

REM Start Municipal App
echo 💻 Εκκίνηση Εφαρμογής...
start "CyberGuard Municipal Edition" python CyberGuard_Municipal_Edition.py

echo.
color 0A
echo ✅ ΤΟ ΣΥΣΤΗΜΑ ΕΙΝΑΙ ΕΤΟΙΜΟ!
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  API Server: http://localhost:5000                    ║
echo ║  Εφαρμογή: Έτοιμη για χρήση                          ║
echo ║  Κλείστε τα παράθυρα για παύση                       ║
echo ╚════════════════════════════════════════════════════════╝
echo.

pause
