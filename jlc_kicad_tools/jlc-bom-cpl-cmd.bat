:: C:\Python3\python C:\Python3\Lib\site-packages\jlc_kicad_tools  C:\Temp\Audio-Mux-dev
:: SET PRJ=D:\Temp\Audio-Mux-dev
set PRJ=%~dp0

cd %PRJ%
echo working on %PRJ% project
C:\Python3\python C:\Python3\Lib\site-packages\jlc_kicad_tools %PRJ%
for %%a in ("%cd%") do set currentfolder=%%~na
echo.%currentfolder%
:: pause

@echo 'delete overlapping components like c_2416 from ' %currentfolder%_cpl_jlc.csv'
@echo 'copy ' %currentfolder%_cpl_jlc.csv' and '%currentfolder%_bom_jlc.csv' to 'gbr' folder

pause