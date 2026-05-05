# ALGOBTC v0.0.1

Базовый терминал на **PySide6** для подключения к Binance и получения цены **BTCUSDT** через WebSocket.

## Что умеет v0.0.1
- Простое GUI-окно `ALGOBTC Terminal`.
- Сохранение Binance API Key / API Secret в `data/config.json`.
- Тест подключения к Binance через безопасный публичный endpoint `/api/v3/time`.
- Запуск/остановка BTCUSDT WebSocket (bookTicker) без блокировки GUI.
- Отображение bid/ask/last/spread/update time в Dashboard.
- Логи ошибок только в `logs/errors.log`.
- Вкладка Algorithms с заготовкой DRY-RUN алгоритма.

## Важно
- В этой версии **нет LIVE-торговли**.
- **Нет ордеров** и исполнения сделок.
- Только подключение, проверка и поток цен.

## Запуск
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

Или через `START.bat`.
