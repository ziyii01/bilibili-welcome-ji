@echo off
if "%1"=="h" goto begin
mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit
:begin
call .venv/Scripts/activate.bat
python main.py