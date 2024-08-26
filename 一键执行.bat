@echo off
REM 设置 Python 可执行文件路径
set PYTHON_EXEC=python


REM 执行 headpdf.py，添加页眉
%PYTHON_EXEC% classify.py

pause


