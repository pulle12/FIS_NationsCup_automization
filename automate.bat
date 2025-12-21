@echo off
setlocal
set PY="%~dp0.venv\Scripts\python.exe"
pushd %~dp0

echo === GUI starten: Viewer und Steuerung ===
%PY% gui.py

echo Hinweis: IDs laden & Scrape bitte in der GUI starten.

popd
echo Fertig. Fenster schliessen mit beliebiger Taste.
pause