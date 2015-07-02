xcopy "block.ico" "..\" /f /Y
cd ..
python .\setup.py build
cd "setup_files"
ren "..\build\exe.win32-3.4" bin
xcopy ..\sound "..\build\bin\sound\" /i /Y 
xcopy *.dll "..\build\bin\*" /f /Y
xcopy "score" "..\build\bin\*" /f /Y
xcopy "Block Game.exe.lnk" "..\build" /Y