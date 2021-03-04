echo OFF

SET PRJ=C:\Temp\myprj
cd %PRJ%
echo working on %PRJ% project

C:\Python3\python C:\Python3\Lib\site-packages\jlc_kicad_tools %PRJ%

pause