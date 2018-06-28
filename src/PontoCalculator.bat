@echo off
del .\__pycache__ /F /Q
del build /F /Q
del dist /F /Q
pyinstaller.exe -i .\PontoCalculator.ico -F --clean --windowed --noupx .\main.py --name PontoCalculator.exe --distpath .\dist 
pause