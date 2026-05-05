@echo off
cd /d %~dp0
echo === FETCH FROM GITHUB ===
git fetch origin
echo === RESET TO origin/main ===
git reset --hard origin/main
echo === CLEAN UNUSED FILES ===
git clean -fd

if not exist .venv (
  echo === CREATE .venv ===
  python -m venv .venv
)

call .venv\Scripts\activate.bat

echo === UPGRADE PIP ===
python -m pip install --upgrade pip --timeout 300 --retries 10 --no-cache-dir

if exist requirements.txt (
  echo === INSTALL requirements.txt ===
  pip install -r requirements.txt --timeout 300 --retries 10 --no-cache-dir
) else (
  echo === INSTALL MINIMUM DEPENDENCIES ===
  pip install PySide6 httpx websockets binance-connector --timeout 300 --retries 10 --no-cache-dir
)

echo === START APP ===
python -m app.main
pause
