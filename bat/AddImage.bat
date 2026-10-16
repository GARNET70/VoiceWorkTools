@echo off
rem setlocal

SET target_path=%1
SET image=%2
SET out_path=%3

echo target_path = %target_path%
echo image = %image%
wcho out_path = %out_path%

ffmpeg -i %target_path% -i %image% -map 0:a -map 1:v -c copy -disposition:1 attached_pic %out_path%
