@echo off
SET rar_path="C:\Program Files\WinRAR\WinRAR.exe"
SET target_path=%1
SET target_folder=%2

rem echo target_path = %1
rem echo target_folder = %2
rem pause

cd /d %target_path%

%rar_path% a -r -ep1 %target_folder% %target_path%%target_folder%/*