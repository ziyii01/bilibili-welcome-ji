@echo off
if "%1"=="h" goto begin
mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit
:begin
REM 你的批处理文件内容
call .venv/Scripts/activate.bat
python main.py