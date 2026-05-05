@echo off
cd /d %~dp0
echo === FETCH FROM GITHUB ===
git fetch origin
echo === RESET TO origin/main ===
git reset --hard origin/main
echo === CLEAN UNUSED FILES ===
git clean -fd
echo === DONE ===
pause
