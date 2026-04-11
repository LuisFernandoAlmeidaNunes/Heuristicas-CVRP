@echo off
py Main.py %* 2>nul && exit /b
python Main.py %* 2>nul && exit /b
python3 Main.py %*