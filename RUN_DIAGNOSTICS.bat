@echo off
cd /d %~dp0
echo === PYTHON ===
python --version
echo === PIP ===
pip --version
echo === GIT ===
git --version

if exist .venv (
  echo .venv: FOUND
) else (
  echo .venv: NOT FOUND
)

echo === IMPORT CHECKS ===
python -c "import PySide6; print('PySide6 OK')"
python -c "import httpx; print('httpx OK')"
python -c "import websockets; print('websockets OK')"
python -c "import binance; print('binance OK')"

echo === BOOTSTRAP CHECK ===
python -c "from app.core.config import bootstrap_files; bootstrap_files(); print('BOOTSTRAP OK')"
pause
