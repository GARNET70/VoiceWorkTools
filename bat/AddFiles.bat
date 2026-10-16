@echo off
SET target_path=%1
SET rarname=%2

rem echo target_path = %1
rem echo rarname = %2

SET rar_path="C:\Program Files\WinRAR\WinRAR.exe"
SET target_rar=%target_path%\%rarname%
SET target_files=%target_path%\*.png %target_path%\*.jpg

rem echo target_rar = %target_rar%
rem echo target_files = %target_files%
rem pause

%rar_path% u -r -ep1 %target_rar% %target_files%