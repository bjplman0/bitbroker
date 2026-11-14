@echo off
setlocal
title BitBroker

cd /d "%~dp0"

echo "%~dp0" | findstr /i /c:"\Temp\Temp1_" >nul
if not errorlevel 1 goto fail_zip

set "PY="
for %%V in (3.14 3.13 3.12 3.11 3.10) do (
    if not defined PY (
        echo n | py -%%V -c "import sys" >nul 2>&1
        if not errorlevel 1 set "PY=py -%%V"
    )
)
if defined PY goto have_python

echo.
echo Nem talaltam Python 3.10 vagy ujabb verziot, telepitem a Python 3.14.5-ot.
echo Csak az aktualis felhasznalonak telepul, admin jog nem kell.
set "INSTALLER=%TEMP%\python-3.14.5-amd64.exe"
curl.exe -L --fail -o "%INSTALLER%" "https://www.python.org/ftp/python/3.14.5/python-3.14.5-amd64.exe"
if errorlevel 1 goto fail_download
start /wait "" "%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_test=0
set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if not exist "%PYEXE%" goto fail_install
del "%INSTALLER%" >nul 2>&1

set PY="%PYEXE%"

:have_python
echo Python: %PY%

if exist ".venv\Scripts\python.exe" goto have_venv
echo Virtualis kornyezet keszitese...
%PY% -m venv .venv
if errorlevel 1 goto fail_venv
:have_venv

if exist ".venv\deps_ok.flag" goto run_game
echo Fuggosegek telepitese, ehhez internet kell...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto fail_pip
echo ok>".venv\deps_ok.flag"

:run_game
echo Jatek inditasa...
".venv\Scripts\python.exe" "src\main.py"
if errorlevel 1 goto fail_game
exit /b 0

rem ================= Hibakezelok =================
:fail_zip
echo.
echo HIBA: a jatek ZIP-bol, kicsomagolas nelkul lett inditva.
echo Csomagold ki a ZIP-et egy normal mappaba - jobb klikk, Osszes kibontasa -
echo es onnan inditsd ujra a run.bat-ot.
goto fail

:fail_download
echo.
echo HIBA: nem sikerult letolteni a Python telepitot. Ellenorizd az internetkapcsolatot,
echo vagy telepitsd kezzel a Python 3.14-et a python.org oldalrol, majd inditsd ujra.
goto fail

:fail_install
echo.
echo HIBA: a Python telepitese nem sikerult. Telepitsd kezzel a Python 3.14-et
echo a python.org oldalrol, majd inditsd ujra a run.bat-ot.
goto fail

:fail_venv
echo.
echo HIBA: nem sikerult letrehozni a virtualis kornyezetet.
echo Torold a .venv mappat, es probald ujra.
goto fail

:fail_pip
echo.
echo HIBA: nem sikerult telepiteni a fuggosegeket. Ellenorizd az internetkapcsolatot,
echo majd inditsd ujra a run.bat-ot.
goto fail

:fail_game
echo.
echo A jatek hibaval allt le, lasd a fenti uzenetet.
goto fail

:fail
echo.
pause
exit /b 1