@echo off
setlocal enabledelayedexpansion

for %%i in (*) do (
    set "filename=%%i"
    ren "%%i" "m!filename!"
)

endlocal
