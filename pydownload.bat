@echo off
echo Please provide your list of mods to be installed as a .txt file.
echo This file should be in the same directory as download.py.
echo This file should have one Modrinth link per line.
echo Commented lines should be preceded with '#'
set /p "txtfile="
set /p "mcver=What version of Minecraft?: "
set /p "modloader=What modloader? (default: fabric): "
python download.py %txtfile% %mcver% %modloader%
pause